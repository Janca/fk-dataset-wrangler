import sys
import time

import tasks

if __name__ == '__main__':
    image_pipeline = tasks.FkPipeline(
        "./input",
        "./output",
        # "F:\\StableDiffusion\\2023_02_24\\images",
        # "F:\\StableDiffusion\\2023_02_24\\output",
        image_ext=".jpg"
    )

    image_filter = tasks.basic.ImageFilter(minimum_dimensions=(320, 320))
    image_scaler = tasks.basic.ImageScaler(768)

    caption_normalizer = tasks.basic.CaptionNormalizer()
    caption_filter = tasks.basic.CaptionFilter()

    blur_filter = tasks.cv.BlurFilter(1200)

    image_pipeline.add_task(caption_normalizer)
    image_pipeline.add_task(caption_filter)

    image_pipeline.add_task(image_filter)
    image_pipeline.add_task(image_scaler)

    image_pipeline.add_task(blur_filter)

    image_pipeline.start()

    try:
        while image_pipeline.active:
            time.sleep(1)

    except KeyboardInterrupt:
        print("Pipeline interrupted.")
        image_pipeline.shutdown()
        sys.exit()

    image_pipeline.shutdown()
