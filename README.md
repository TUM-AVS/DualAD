# DualAD: Dual-Layer Planning for Autonomous Driving
 
# (The code cleaning is still in progress!)

<div align='center'>

![DualAD Framework](./assets/teaser.png)

🌍 [Project Page](https://dualad.github.io/) • 🤓 [Paper](https://arxiv.org/pdf/2409.18053) 

</div>

[**TL;DR**] DualAD is an autonomous driving framework that integrates reasoning capabilities (large language models) with traditional planning modules (rule-based) to handle complex driving scenarios. 

## Installation
- Setup the nuPlan dataset as described [HERE](https://nuplan-devkit.readthedocs.io/en/latest/dataset_setup.html). Make sure you have a general filesystem hierarchy like this (nuplan is at the same level as DualAD's working directory)
   ```bash
   # echo ${HOME} to see what is it
   ${HOME}/nuplan
   ├── exp
   └── dataset
      ├── maps
      └── nuplan-v1.1
   ${HOME}/DualAD
   ```
- Quick install to try DualAD using miniconda:
   ```bash
   git clone https://github.com/TUM-AVS/DualAD.git
   cd DualAD
   conda create -n dualad python=3.9
   conda activate dualad
   pip install -e .
   pip install -r requirements_torch.txt
   pip install -r requirements.txt
   # Set env variable
   . set_env.sh
   ```

## Get LLM API (You can skip this to first run the code without LLM)
GLM-4-Flash ([FREE](https://open.bigmodel.cn/pricing)) and [GPT-4o](https://platform.openai.com/settings/organization/api-keys) ([Need to pay](https://openai.com/api/pricing/)). For example, the API keys look like below (if you have problem with getting the free one (GLM-4-Flash), feel free to contact dingrui.wang@tum.de)

   ```bash
   # GLM-4-Flash
   7e8138a27b2cd87c7691ac4a7XXXXXXXXXXXXXXXXXXXXXX
   # GPT-4o
   sk-proj-IDX3WOWAk28xifvCyXXXXXXXXXXXXXXXXXXXXXX
   ```
In ```nuplan/planning/simulation/planner/abstract_idm_planner.py line: 327```, add your API key and set ```use_llm``` to ```True```.
## Try DualAD
For DualAD (Lattice-IDM):
   ```bash
   python ./nuplan/planning/script/run_simulation.py
   ```

## Performance

DualAD demonstrates improved performance in challenging scenarios compared to other planners. Key metrics such as **Closed-Loop Score (CLS)** and **Reactive Closed-Loop Score (R-CLS)** showcase DualAD’s ability to outperform rule-based and learning-based models in terms of safety and decision quality.

| Planner                  | Hard-55 CLS | Super-Hard-24 CLS |
|--------------------------|-------------|--------------------|
| IDM                      | 50.12       | 34.56             |
| Lattice-IDM              | 52.36       | 39.76             |
| **DualAD (Lattice-IDM)** | **60.25**   | **57.31**         |





## Credits

- [https://github.com/motional/nuplan-devkit](https://github.com/motional/nuplan-devkit)
- [https://github.com/huggingface/huggingface_hub](https://github.com/huggingface/huggingface_hub)
- [https://github.com/autonomousvision/tuplan_garage](https://github.com/autonomousvision/tuplan_garage)
- [https://github.com/jchengai/planTF](https://github.com/jchengai/planTF)