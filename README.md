# Deja - 2025 NASA Space Apps Challenge - Meteor Madness

## Overview
Impactor-2025 has been spotted! We do not know its full characteristics, but how can we
tell the public about its dangers?

This project aims to simulate the damages an asteroid can have. By selecting one of the few
Near Earth Objects (NEO), users can intuitively visualize the impact and be alerted!

For those who are interested, check our [website](https://deja.earth/).

For the tech savvy among us, keep reading!

## Installation
A simple `git clone` to clone the project
```sh

git clone https://github.com/leejiaq/Deja-NASA-Space-Apps-Challenge-2025
```

Then navigate to `backend` to initialize our project.
A project manager is needed here; we recommend `uv`.

```sh 
cd backend
uv init
uv sync
```

## Usage
To use the front end, simply compile using `npm`.

``` sh
cd frontend
npm install
npm run dev
```

To use the back end, run the following commands.

``` sh 
cd backend
source .venv/bin/activate
uvicorn api:app --reload
```


## Acknowledgements
Part of the impact simulation is [Earth Impact Effects Program](https://impact.ese.ic.ac.uk/ImpactEarth) and its specifications

