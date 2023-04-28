# fk-dataset-wrangler
*a fking dataset wrangler*

Normalize image dataset and filter based on a variety of growing options

## Usage
```commandline
usage: main.py [-h] [--output-image-ext OUTPUT_IMAGE_EXT]
               [--output-caption-text-ext OUTPUT_CAPTION_TEXT_EXT]
               [--resource-usage {low,med,high,make-my-pc-hurt}]
               [--require-caption-text] [--required-tags REQUIRED_TAGS]
               [--blacklisted-tags BLACKLISTED_TAGS] [--normalize-captions]
               [--minimum-dimensions MINIMUM_DIMENSIONS]
               [--maximum-dimensions MAXIMUM_DIMENSIONS] [--modes MODES]
               [--scale SCALE] [--jpeg-quality JPEG_QUALITY]
               [--blur-threshold BLUR_THRESHOLD]
               [--entropy-threshold ENTROPY_THRESHOLD]
               [--chad-score CHAD_SCORE]
               src dst

positional arguments:
  src                   dataset input folder
  dst                   dataset output folder

options:
  -h, --help            show this help message and exit
  --output-image-ext OUTPUT_IMAGE_EXT
                        extension to use when saving images to the dataset
                        output folder (default: .png)
  --output-caption-text-ext OUTPUT_CAPTION_TEXT_EXT
                        extension to use when saving image caption text to the
                        dataset output folder (default: .txt)
  --resource-usage {low,med,high,make-my-pc-hurt}
                        configure pipeline to use more or less resources
                        (default: low)

CaptionFilter options:
  --require-caption-text
                        require caption text file to exist and be non-empty
                        (default: False)
  --required-tags REQUIRED_TAGS
                        discard image if the caption text does not contain one
                        or more of the provided tags; tags can be provided in
                        a comma-separated list (default: None)
  --blacklisted-tags BLACKLISTED_TAGS
                        discard image if the caption text contains one or more
                        of the provided tags; tags can be provided in a comma-
                        separated list (default: None)

CaptionNormalizer options:
  --normalize-captions  normalize captions by removing weights, punctuation
                        and extraneous symbols; (default: False)

ImageFilter options:
  --minimum-dimensions MINIMUM_DIMENSIONS
                        image dimensions must be this size or larger, or be
                        discarded (example: 320x320; default: None)
  --maximum-dimensions MAXIMUM_DIMENSIONS
                        image dimensions must be this size or smaller, or be
                        discarded (example: 1024x1024; default: None)
  --modes MODES         discard image if mode does not match provided modes;
                        modes can be provided in a comma-separated list
                        (default: None [disabled])

ImageScaler options:
  --scale SCALE         scale image to the provided size, keeping aspect ratio
                        (default: -1 [disabled])

JPGQualityFilter options:
  --jpeg-quality JPEG_QUALITY
                        discard images if they are not at least the provided
                        quality level (0 - 100; default: -1 [disabled])

BlurFilter options:
  --blur-threshold BLUR_THRESHOLD
                        discard image if image does not meet blur threshold (0
                        - infinite; 0 = most blurry; default: -1 [disabled])

EntropyFilter options:
  --entropy-threshold ENTROPY_THRESHOLD
                        discard image if image does not meet entropy threshold
                        (0 - 8; 0 = least entropic; 8 = most entropic;
                        default: -1 [disabled])

CHADScoreFilter options:
  --chad-score CHAD_SCORE
                        discard image if image does not meet aesthetic score
                        (0 - 8; 0 = least aesthetic; 8 = most aesthetic;
                        default: -1 [disabled])
```