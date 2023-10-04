from typing import List, Tuple
import os

import numpy as np
import cv2



class VideoProcessing():
    """
    Process video including:
    - load: 
        Load video and return list of frames

    - sampling: 
        Choose 1 frame every n frames

    - truncating: 
        Equally trim both head and tail if video length > max_frame

    - padding: 
        Pad black frame to end of video if video length < min_frame

    - resize: 
        Change size of a video
    
    - auto: 
        Auto apply: Load -> Sampling -> Balancing -> Resize
    """

    def __init__(
            self, 
            sampling_value: int, 
            max_frames: int, 
            min_frames: int, 
            size: Tuple[int, int]
        ) -> None:
        self.sampling_value = sampling_value
        self.max_frames = max_frames
        self.min_frames = min_frames
        self.size = size


    def __call__(self, path: str) -> List[np.ndarray]:
        """
        Object call, apply auto(x) in return
        """
        return self.auto(path)


    def load(self, path: str) -> List[np.ndarray]:
        """
        Load video and return list of frames
        """
        if not os.path.exists(path):
            raise FileExistsError("File not found!")
        video = cv2.VideoCapture(path)
        if not video.isOpened():
            raise RuntimeError("Could not open video file.")
        output = [
            cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) for _, frame in iter(video.read, (False, None))
        ]
        video.release()
        return output


    def sampling(self, video: np.ndarray, value: int) -> np.ndarray:
        """
        Reduce video size by choose 1 frame every n frame (n = value)
        """
        return video[::value] if value else video


    def truncating(self, video: np.ndarray, max_frame: int) -> np.ndarray:
        """
        Cut both head and last if video length > max_frame
        Output is the middle of the source video
        """
        if max_frame > 0:
            middle_frame = len(video) // 2
            m = max_frame // 2
            r = max_frame % 2
            video = video[middle_frame - m : middle_frame + m + r]
        return video


    def padding(self, video: np.ndarray, min_frame: int) -> np.ndarray:
        """
        Pad black frame to end of video if video length < min_frame
        """
        if min_frame > 0:
            zeros_array = np.zeros((min_frame, *video.shape[1:]), dtype=np.uint8)
            zeros_array[:len(video), ...] = video
            video = zeros_array
        return video


    def resize(self, video: np.ndarray, size: Tuple[int, int]) -> np.ndarray:
        """
        Change size of a video
        """
        return np.array([cv2.resize(frame, size) for frame in video])


    def auto(self, path: np.ndarray) -> List[np.ndarray]:
        """
        Auto apply: Load -> Sampling -> Truncating -> Padding -> Resize
        """
        video = self.load(path)
        video = self.sampling(video, self.sampling_value)
        video = self.truncating(video, self.max_frames)
        video = self.padding(video, self.min_frames)
        video = self.resize(video, self.size)
        return video