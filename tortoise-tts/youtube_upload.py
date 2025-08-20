import os
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import googleapiclient.http

#scopes define the permissions needed for YouTube upload
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

#get absolute path to this script file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

#path to the client_secret.json file (used for OAuth authentication)
CLIENT_SECRETS_FILE = os.path.join(BASE_DIR, "client_secret.json")  #change this if your file name/path is different

#function to upload a video to YouTube
def upload_video(video_file, title, description, thumbnail_file=None):
    #allow HTTP for local testing (do not use in production)
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    #authenticate user and create OAuth 2.0 credentials
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, SCOPES)
    credentials = flow.run_local_server(port=0)

    #build YouTube API client using the credentials
    youtube = googleapiclient.discovery.build(
        "youtube", "v3", credentials=credentials)

    #prepare request body with metadata
    request_body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": ["bedtime story", "sleep", "black screen", "calm narration"],
            "categoryId": "22"  #category 22 = People & Blogs
        },
        "status": {
            "privacyStatus": "public",  #video visibility: public, unlisted, or private
            "madeForKids": True         #specify if video is made for kids
        }
    }

    #prepare media upload object with the video file
    media_file = googleapiclient.http.MediaFileUpload(video_file, chunksize=-1, resumable=True)

    print("Uploading video...")
    request = youtube.videos().insert(
        part="snippet,status",
        body=request_body,
        media_body=media_file
    )

    #upload video in chunks
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Upload progress: {int(status.progress() * 100)}%")

    #print upload success message with video link
    print("Video upload complete!")
    video_id = response.get("id")
    video_url = f"https://youtu.be/{video_id}"
    print(f"Video ID: {video_id}")
    print(f"Watch it here: {video_url}")

    #optional: upload thumbnail image if provided
    if thumbnail_file and os.path.exists(thumbnail_file):
        print("Uploading thumbnail...")
        youtube.thumbnails().set(
            videoId=video_id,
            media_body=googleapiclient.http.MediaFileUpload(thumbnail_file)
        ).execute()
        print("Thumbnail uploaded!")

    return video_url  #return URL for use in the GUI or terminal
