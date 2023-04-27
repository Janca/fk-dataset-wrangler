import sys
import time

import tasks

if __name__ == '__main__':
    image_pipeline = tasks.FkPipeline(
        "E:\\StableDiffusion\\SD Datasets\\CivitAI\\2023_03_18\\dataset",
        "E:\\StableDiffusion\\SD Datasets\\CivitAI\\2023_03_18\\output",
        image_ext=".jpg"
    )

    low_resource_task_pool_size = 20
    med_resource_task_pool_size = 10
    high_resource_task_pool_size = 5
    gpu_resource_task_pool_size = 1

    caption_normalizer = tasks.basic.CaptionNormalizer()
    caption_filter = tasks.basic.CaptionFilter()

    image_pipeline.add_task(caption_normalizer, max_workers=low_resource_task_pool_size)
    image_pipeline.add_task(caption_filter, max_workers=low_resource_task_pool_size)

    image_filter = tasks.basic.ImageFilter(minimum_dimensions=(320, 320))
    image_scaler = tasks.basic.ImageScaler(768)

    image_pipeline.add_task(image_filter, max_workers=low_resource_task_pool_size)
    image_pipeline.add_task(image_scaler, max_workers=low_resource_task_pool_size)

    blur_filter = tasks.cv.BlurFilter(1200)
    entropy_filter = tasks.cv.EntropyFilter(7.5)

    image_pipeline.add_task(blur_filter, max_workers=med_resource_task_pool_size)
    image_pipeline.add_task(entropy_filter, max_workers=high_resource_task_pool_size)

    chad_filter = tasks.openclip.CHADScoreFilter(7.25)

    image_pipeline.add_task(chad_filter, max_workers=gpu_resource_task_pool_size)

    image_pipeline.start()

    try:
        print("Waiting for workers to complete...")
        while image_pipeline.active:
            time.sleep(1)

    except KeyboardInterrupt:
        print("Pipeline interrupted.")
        image_pipeline.shutdown()
        sys.exit()

    print("Shutting down pipeline...")
    image_pipeline.shutdown()
