# Helldivers 2 - Stratagem Macros

This Python script manages stratagems for Helldivers 2. Developed in response to the absence of native support for Corsair macro functionalities in Linux, this project provides a tailored solution to enhance gaming efficiency. Designed as both a personal utility and a programming exercise, this script enables gamers to create, modify, and execute game macros by binding them to other keys on the keyboard. It represents an application of my programming skills to meet specific gaming needs, and I hope it proves beneficial to others as well.

## Prerequisites

- Python 3.8 or higher

## Installation

To install the script, follow these steps:

1. Clone the repository:
    ```
    https://github.com/routaran/hd2_macros.git
    ```
2. Navigate to the project directory:
    ```
    cd hd2_macros
    ```
Continue with the following steps if you wish to run the python script instead of the precompiled Windows executable.

3. Create a virtual environment:
    ```
    python -m venv env
    ```
4. Activate the virtual environment:
    - On Windows:
        ```
        .\env\Scripts\activate
        ```
    - On Unix or MacOS:
        ```
        source env/bin/activate
        ```
5. Install the dependencies:
    ```
    pip install -r requirements.txt
    ```

## Usage

To use the program:

1. Launch via Python:
    ```
    python gui.py
    ```
Alternatively:

1. Run the precompiled Windows executable; json files MUST be in the same folder as the executable. You can move the executable anywhere you want, as long as it is with the 2 json files. I tested this on my Win10x64 and it worked, not sure about compatibility as I don't have access to other versions of Windows but it should work.
    ```
    stratagems.exe
    ```

2. The program will open a GUI where you can manage your stratagems.

3. You can add a new stratagem by clicking the "Add Stratagem" button and entering the name and keys of the stratagem.

4. You can edit an existing stratagem by clicking the "Edit Stratagem" button, selecting the stratagem to edit, and entering the new keys.

5. You can delete an existing stratagem by clicking the "Delete Stratagem" button and selecting the stratagem to delete. If the stratagem is currently bound to a macro, the macro will be set to "Unassigned".

6. If you make a mistake and accidentally delete stratagems, you can restore the original setup by downloading and replacing the stratagem.json file from the repository. This allows you to revert back to the original stratagems without having to manually re-enter them.

7. You will need to ensure that your stratagem key is set to Left Control and you remap the stratagem arrows to i, j, k, l corresponding to Up, Left, Down, Right.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[GPL-3](https://www.gnu.org/licenses/gpl-3.0.en.html)
