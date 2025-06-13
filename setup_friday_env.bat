@echo off
echo -----------------------------------------------------
echo Creating virtual environment...
python -m venv venv

echo -----------------------------------------------------
echo Activating virtual environment...
call venv\Scripts\activate

echo -----------------------------------------------------
echo Upgrading pip...
python -m pip install --upgrade pip

echo -----------------------------------------------------
echo Installing required packages...
pip install moviepy fer opencv-python mediapipe

echo -----------------------------------------------------
echo Testing moviepy.editor module...
python -c "import moviepy.editor; print('moviepy.editor imported successfully')"

echo -----------------------------------------------------
echo All done! Your virtual environment is ready.
pause
