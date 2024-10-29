import logging
import os
from pathlib import Path
from shutil import rmtree
from typing import List, Optional, Union

import hydra
import pytorch_lightning as pl
from omegaconf import DictConfig, OmegaConf

from nuplan.common.utils.s3_utils import is_s3_path
from nuplan.planning.script.builders.simulation_builder import build_simulations
from nuplan.planning.script.builders.simulation_callback_builder import (
    build_callbacks_worker,
    build_simulation_callbacks,
)
from nuplan.planning.script.utils import run_runners, set_default_path, set_up_common_builder
from nuplan.planning.simulation.planner.abstract_planner import AbstractPlanner

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# If set, use the env. variable to overwrite the default dataset and experiment paths
set_default_path()

# If set, use the env. variable to overwrite the Hydra config
CONFIG_PATH = os.getenv('NUPLAN_HYDRA_CONFIG_PATH', 'config/simulation')

if os.environ.get('NUPLAN_HYDRA_CONFIG_PATH') is not None:
    CONFIG_PATH = os.path.join('../../../../', CONFIG_PATH)

if os.path.basename(CONFIG_PATH) != 'simulation':
    CONFIG_PATH = os.path.join(CONFIG_PATH, 'simulation')
CONFIG_NAME = 'default_simulation'


def run_simulation(cfg: DictConfig, planners: Optional[Union[AbstractPlanner, List[AbstractPlanner]]] = None) -> None:
    """
    Execute all available challenges simultaneously on the same scenario. Helper function for main to allow planner to
    be specified via config or directly passed as argument.
    :param cfg: Configuration that is used to run the experiment.
        Already contains the changes merged from the experiment's config to default config.
    :param planners: Pre-built planner(s) to run in simulation. Can either be a single planner or list of planners.
    """
    # Fix random seed
    pl.seed_everything(cfg.seed, workers=True)

    profiler_name = 'building_simulation'
    common_builder = set_up_common_builder(cfg=cfg, profiler_name=profiler_name)

    # Build simulation callbacks
    callbacks_worker_pool = build_callbacks_worker(cfg)
    callbacks = build_simulation_callbacks(cfg=cfg, output_dir=common_builder.output_dir, worker=callbacks_worker_pool)

    # Remove planner from config to make sure run_simulation does not receive multiple planner specifications.
    if planners and 'planner' in cfg.keys():
        logger.info('Using pre-instantiated planner. Ignoring planner in config')
        OmegaConf.set_struct(cfg, False)
        cfg.pop('planner')
        OmegaConf.set_struct(cfg, True)

    # Construct simulations
    if isinstance(planners, AbstractPlanner):
        planners = [planners]

    runners = build_simulations(
        cfg=cfg,
        callbacks=callbacks,
        worker=common_builder.worker,
        pre_built_planners=planners,
        callbacks_worker=callbacks_worker_pool,
    )

    if common_builder.profiler:
        # Stop simulation construction profiling
        common_builder.profiler.save_profiler(profiler_name)

    logger.info('Running simulation...')
    run_runners(runners=runners, common_builder=common_builder, cfg=cfg, profiler_name='running_simulation')
    logger.info('Finished running simulation!')


def clean_up_s3_artifacts() -> None:
    """
    Cleanup lingering s3 artifacts that are written locally.
    This happens because some minor write-to-s3 functionality isn't yet implemented.
    """
    # Lingering artifacts get written locally to a 's3:' directory. Hydra changes
    # the working directory to a subdirectory of this, so we serach the working
    # path for it.
    working_path = os.getcwd()
    s3_dirname = "s3:"
    s3_ind = working_path.find(s3_dirname)
    if s3_ind != -1:
        local_s3_path = working_path[: working_path.find(s3_dirname) + len(s3_dirname)]
        rmtree(local_s3_path)


@hydra.main(config_path=CONFIG_PATH, config_name=CONFIG_NAME)
def main(cfg: DictConfig) -> None:
    """
    Execute all available challenges simultaneously on the same scenario. Calls run_simulation to allow planner to
    be specified via config or directly passed as argument.
    :param cfg: Configuration that is used to run the experiment.
        Already contains the changes merged from the experiment's config to default config.
    """


    assert cfg.simulation_log_main_path is None, 'Simulation_log_main_path must not be set when running simulation.'

    # Execute simulation with preconfigured planner(s).
    run_simulation(cfg=cfg)

    if is_s3_path(Path(cfg.output_dir)):
        clean_up_s3_artifacts()

import tempfile
if __name__ == '__main__':


    # Location of path with all simulation configs
    CONFIG_PATH = '../script/config/simulation'
    CONFIG_NAME = 'default_simulation'
    # Get the checkpoint of the trained model
 # Create a temporary directory to store the cache and experiment artifacts
    SAVE_DIR = Path(tempfile.gettempdir()) / 'tutorial_nuplan_framework'  # optionally replace with persistent dir
    # Name of the experiment
    EXPERIMENT = 'simulation_urban_experiment'
    JOB_NAME = 'train_default_urban'
    LOG_DIR = SAVE_DIR / EXPERIMENT / JOB_NAME

    # Select the planner and simulation challenge
    CHALLENGE = 'closed_loop_nonreactive_agents'  # [open_loop_boxes, closed_loop_nonreactive_agents, closed_loop_reactive_agents]
    DATASET_PARAMS = [
        'scenario_builder=nuplan_mini',  # use nuplan mini database
        'scenario_filter=SuperHard',  # superHard rethinking-hard initially select all scenarios in the database
        # 'scenario_filter.scenario_types=[high_magnitude_speed]',  # select scenario types
        # 'scenario_filter.num_scenarios_per_type=20',  # use 10 scenarios per scenario type
    ]
    # [starting_straight_traffic_light_intersection_traversal, high_lateral_acceleration, changing_lane, high_magnitude_speed, low_magnitude_speed, starting_left_turn, starting_right_turn, stopping_with_lead, following_lane_with_lead, near_multiple_vehicles, traversing_pickup_dropoff, behind_long_vehicle, waiting_for_pedestrian_to_cross, stationary_in_traffic]
    # Name of the experiment

    MODEL_PATH = "/home/f1tenth/nuplan-devkit/checkpoints/urban_driver_open_loop.ckpt"



    # Initialize configuration management system
    hydra.core.global_hydra.GlobalHydra.instance().clear()  # reinitialize hydra if already initialized
    hydra.initialize(config_path=CONFIG_PATH)

    # Compose the configuration
    cfg = hydra.compose(config_name=CONFIG_NAME, overrides=[
        f'experiment_name={EXPERIMENT}',
        f'group={SAVE_DIR}',
        'planner=ml_planner',
        'model=urban_driver_open_loop_model',
        'planner.ml_planner.model_config=${model}',  # hydra notation to select model config
        f'planner.ml_planner.checkpoint_path={MODEL_PATH}',  # this path can be replaced by the checkpoint of the model trained in the previous section
        f'+simulation={CHALLENGE}',
        *DATASET_PARAMS,
    ])
    main(cfg)


