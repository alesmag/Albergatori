<h1 align="center">Booking Albergatori</h1>

<p align="center">
  <em>University Project</em>
</p>

<p align="center">
  <strong>Built with:</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=FFD43B" alt="Python">
  <img src="https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black" alt="JavaScript">
  <img src="https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white" alt="CSS">
  <img src="https://img.shields.io/badge/HTML-E34F26?style=for-the-badge&logo=html5&logoColor=white" alt="HTML">
</p>

---

## Table of Contents

- [About the Project](#about-the-project)
- [Features](#features)
- [Requirements](#requirements)
- [Usage](#usage)

## About the Project
Booking Albergatori is a group project developed by [Me](https://github.com/alesmag), [Anna Chiara Mameli](https://github.com/Pandanna), [Alessio Gallo](https://github.com/ale-gll) and [Noemi Cabras](https://github.com/noemicabrasss) for the University of Cagliari. 
This project was intended to be a reservation website for hotels.

## Features

Users can sign-up or log-in depending if they want to be a normal user (one who reserves) or a host (one who puts hotels and rooms up). 
Normal users can see and look up hotels and rooms, they can reservate one or more of them and they can choose which days they will stay in a specific room. They can also see their present and past reservations. Finally, they can also cancel a reservation as long as it falls under a 10 days minimum notice (after which would be impossible to cancel).

Hosts can put up hotels and their respective rooms, set their price and their availability. They can also see their hotels and rooms, modify them or even delete them from the website. 

More details can be found in the "Project Description" document.

## Requirements

This project requires:
- pip
- python

### Installation

#### Ubuntu/Debian
```sh
sudo apt update && sudo apt install -y python-pip python
```

#### Fedora
```sh
sudo dnf install -y python-pip python
```

#### macOS (Homebrew):
```sh
brew install python-pip python
```

To install the missing dependencies, run:
```sh
pip install -r requirements.txt
```

## Usage
The following commands need to be run inside albergatori/ folder.

### Running the project

To run the project, run:
```sh
python3 manage.py runserver
```

To access the website, paste the following URL in a web browser:
```sh
http://127.0.0.1:8000/booking/login/
```

### Testing the project
To test the project with Selenium, run:
```sh
python3 manage.py test booking
```
