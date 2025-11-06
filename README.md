# 🤖 Chess Bot and Application

An A-Level Computer Science project that implements a functional chess application with an integrated AI engine, a graphical user interface, and user management features. The application is designed to help members of the **Wirral Grammar School for Boys** chess club learn, practice, and improve their gameplay.

---

## 🧭 Table of Contents

* [🌟 Features](#-features)
    * [Core Features](#core-features)
    * [User Experience & Persistence Features](#user-experience--persistence-features)
* [🛠️ Technologies & Algorithms](#%EF%B8%8F-technologies--algorithms)
    * [Primary Technologies](#primary-technologies)
    * [Key Algorithms & Structures](#key-algorithms--structures)
* [🏃 Getting Started](#-getting-started)
    * [Prerequisites](#prerequisites)
    * [Installation](#installation)
    * [Running the Application](#running-the-application)
* [💡 Further Development](#-further-development)
* [👨‍💻 Project Overview](#-project-overview)

---

## 🌟 Features

This application includes both core gameplay functionality and several features designed to enhance the user experience and training.

### Core Features

* **Chess Engine (The Bot)**: An AI built using a **Minimax algorithm** enhanced with **Alpha-Beta Pruning** and **Quiescence Searching** for move evaluation.
    * The engine's evaluation heuristic considers **Material Advantage**, **Positional Advantage**, and **Strategical Advantage** (including King Safety, Mobility, and Pawn Structure).
* **Bit-Board Representation**: The chessboard state is represented using **64-bit binary integers** (**Bit-boards**) for highly efficient move generation and manipulation.
* **Game Modes**:
    * **Player vs. Player (PvP)** (Local).
    * **Player vs. Computer (PvC)**: Play against the integrated AI engine.
    * **Computer vs. Computer (CvC)**.
    * **Online PvP**: Multiplayer functionality achieved via **client-server architecture**.
    * **Analysis/Sandbox Mode**: Allows users to set up a board position and request the engine's best move and evaluation.
* **Full Chess Rules**: Includes implementation of special rules such as **Castling**, **En Passant**, and **Pawn Promotion**.

### User Experience & Persistence Features

* **Graphical User Interface (GUI)**: Built using the **Pygame** library, providing a responsive and intuitive interface.
* **User Authentication**: A secure system for account creation and login, with passwords **hashed** and **encrypted** for security.
* **Data Persistence (SQL)**: Stores user data, game records, and engine information in a **MySQL database**.
* **Offline Support**: Users can automatically load an **anonymous account** and save games locally if no connection is secured.
* **
### ⬇️ Downloadable Project Write-up

For the best experience, download the original document file:
[Download Full Project PDF](./non_program/FINISHED%20NEA%20Eric%20Zhou.pdf)
