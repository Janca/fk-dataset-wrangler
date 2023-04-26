import time

import tasks.basic

if __name__ == '__main__':
    image_pipeline = tasks.FkPipeline("./input", "./output", image_ext=".jpg")

    image_filter = tasks.basic.ImageFilter(minimum_dimensions=(320, 320))
    image_scaler = tasks.basic.ImageScaler(768)

    caption_normalizer = tasks.basic.CaptionNormalizer()
    caption_filter = tasks.basic.CaptionFilter()

    image_pipeline.add_task(caption_normalizer)
    image_pipeline.add_task(caption_filter)

    image_pipeline.add_task(image_filter)
    image_pipeline.add_task(image_scaler)

    image_pipeline.start()

    try:
        while image_pipeline.active:
            time.sleep(1)
    except KeyboardInterrupt:
        image_pipeline.shutdown()

    image_pipeline.shutdown()
