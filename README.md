# normalizeData

To run the pipeline.py 

One-time setup:
brew install ffmpeg
pip install opencv-contrib-python - or pip install -r requirements.txt
Download EDSR_4.pb and place it in the project root (find it in the opencv_contrib repo releases)

Create a folder named videos
Put your .mp4 files inside it
Every run:
1. Put your mp4 files in the videos/ folder
2. Run python pipeline.py
3. Collect results from final_videos/

Running on Google Colab (colab_pipeline.ipynb)
Steps
Go to https://colab.research.google.com
Click File → Upload notebook
Upload colab_pipeline.ipynb