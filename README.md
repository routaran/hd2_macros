# Helldivers 2 - Strategem Macros

This is a Python program for managing strategems.

## Prerequisites

- Python 3.8 or higher

## Installation

1. Clone the repository:
    ```
    https://github.com/routaran/hd2_macros.git
    ```
2. Navigate to the project directory:
    ```
    cd hd2_macros
    ```

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
1. Run the program:
    ```
    python gui.py
    ```

Alternatively, run via python:
1. Run the precompiled Windows executable, json files MUST be in the same folder as the executable. You can move the executable anywhere you want, as long as it is with the 2 json files. 
   I tested this on my Win10x64 and it worked, not sure about compatibility as I don't have access to other versions of Windows but it should work.
    ```
    strategems.exe
    ```
2. The program will open a GUI where you can manage your strategems.

3. You can add a new strategem by clicking the "Add Strategem" button and entering the name and keys of the strategem.

4. You can edit an existing strategem by clicking the "Edit Strategem" button, selecting the strategem to edit, and entering the new keys.

5. You can delete an existing strategem by clicking the "Delete Strategem" button and selecting the strategem to delete. If the strategem is currently bound to a macro, the macro will be set to "Unassigned".

6. If you make a mistake and accidentally delete strategems, you can restore the original setup by downloading and replacing the strategem.json file from the repository. This allows you to revert back to the original strategems without having to manually re-enter them.  

7. You will need to ensure that your strategem key is set to Left Control and you remap the strategem arrows to i, j, k, l corresponding to Up, Left, Down, Right.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[GPL-3](https://www.gnu.org/licenses/gpl-3.0.en.html)
