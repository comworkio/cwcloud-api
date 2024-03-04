# GitOps with FluxCD and Helm Charts

Welcome to comwork cloud. Here you'll find the Helm charts that will configure your Kubernetes application.

This repository consists of an Umbrella chart and subcharts inside `charts` directory

![cloud_bg](https://gitlab.comwork.io/comwork_public/comwork_cloud/-/raw/main/img/cloud_bg.png)

### Approach to make changes

1. Make changes

2. Update version of the umbrella chart in its `Chart.yaml`

3. Optional: Update the version of the sub-chart (`postgresql` for example) in its `Chart.yaml` file and in the dependencies section in the Umbrella's `Chart.yaml`

### Extra

You can check our public documentation [here](https://gitlab.comwork.io/comwork_public/comwork_cloud)
