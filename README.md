This repository started as a fork of [s3fifo.py](https://github.com/cmcaine/s3fifo.py), but I changed enough of the original code that I decided to remove most of it.
Credit to [cmcaine](https://github.com/cmcaine) for coming up with the Python code for S3-FIFO, which I used as a base for the adaptations that I made.

I wrote a [blog post](https://sidhion.com/blog/posts/function-image-eviction/) explaining why this code exists.

The file `plots.py` creates the plots I used in the blog post. Given that the dataset I used to generate the data for the plots is very heavy, you'll have to download it on your own and use the `process_azure_functions*.py` files to process the dataset before using it with `tests_invocations.py`. Contact me if you need help figuring this out.
