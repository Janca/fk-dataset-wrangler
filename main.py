import sys
import time

import tasks

_TASK_POOL_SIZES = {
    "low": (10, 5, 1, 1),
    "med": (20, 10, 5, 1),
    "high": (30, 15, 10, 1),
    "make-my-pc-hurt": (60, 40, 20, 2)
}

if __name__ == '__main__':

    input_folder = "./input"
    output_folder = "./output"

    image_pipeline = tasks.FkPipeline(
        input_folder,
        output_folder,
        image_ext=".png"
    )

    task_pool_sizes = _TASK_POOL_SIZES["make-my-pc-hurt"]

    low_resource_task_pool_size, med_resource_task_pool_size, \
        high_resource_task_pool_size, gpu_resource_task_pool_size = task_pool_sizes

    caption_normalizer = tasks.basic.CaptionNormalizer()
    caption_filter = tasks.basic.CaptionFilter(
        require_caption_text=False
    )

    image_pipeline.add_task(caption_normalizer, max_workers=low_resource_task_pool_size)
    image_pipeline.add_task(caption_filter, max_workers=low_resource_task_pool_size)

    jpg_quality_filter = tasks.basic.JPGQualityFilter(75)
    image_filter = tasks.basic.ImageFilter(minimum_dimensions=(512, 512))
    image_scaler = tasks.basic.ImageScaler(896)

    image_pipeline.add_task(jpg_quality_filter, max_workers=low_resource_task_pool_size)
    image_pipeline.add_task(image_filter, max_workers=low_resource_task_pool_size)
    image_pipeline.add_task(image_scaler, max_workers=low_resource_task_pool_size)

    blur_filter = tasks.cv.BlurFilter(475)
    entropy_filter = tasks.cv.EntropyFilter(4.75)

    image_pipeline.add_task(blur_filter, max_workers=med_resource_task_pool_size)
    image_pipeline.add_task(entropy_filter, max_workers=high_resource_task_pool_size)

    chad_filter = tasks.openclip.CHADScoreFilter(4.75)

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
