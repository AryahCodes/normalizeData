# normalizeData

Normalizes videos to 60fps and 1280x720 resolution. Videos are scaled to exactly 1280x720 regardless of original size.

I suggest you run on the Google Colab as it will be faster.
Running on Google Colab (colab_pipeline.ipynb)

Before opening Colab:
1. Upload all your .mp4 files to a folder called "AppDevInputVids" in your Google Drive
2. In your Google Drive have a folder called "AppDevOutputVids"
3. You can change the folder names or the input path and output path at cell 4 in the ipybn file. 

In Colab:
1. Go to https://colab.research.google.com
2. Click File → Upload notebook → upload colab_pipeline.ipynb
3. Run Cell 1: installs ffmpeg
4. Run Cell 2: upload pipeline.py from your computer
5. Run Cell 3: mounts Google Drive (will ask you to authorize)
6. Run Cell 4: processes all videos - reads from MyDrive/AppDevInputVids/, writes to MyDrive/AppDevOutputVids/

Results are saved directly to your Google Drive — no downloading needed.
If your Drive folder has a different name, edit VIDEOS_DIR in Cell 3.


Now to run pipeline.py locally:
One-time setup:
brew install ffmpeg

Every run:
1. Run python pipeline.py once — it will auto-create input_vids/ and final_vids/
2. Put your .mp4 files in input_vids/
3. Run python pipeline.py again
4. Collect results from final_vids/
