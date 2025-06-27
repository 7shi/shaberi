# [lightblue/tengu_bench]
# 1048/119=8.81 o4-mini/gemini-2.5-pro-preview-05-06
# 1042/119=8.76 o4-mini/gemini-2.5-pro-preview-03-25
# 1004/119=8.44 o4-mini/gemini-2.5-flash

time uv run tengu.py ../../data/model_answers/lightblue__tengu_bench/gemini-2.5-flash.json -m o4-mini --disable-temperature --all
time uv run tengu.py ../../data/model_answers/lightblue__tengu_bench/gemini-2.5-pro-preview-03-25.json -m o4-mini --disable-temperature --all
time uv run tengu.py ../../data/model_answers/lightblue__tengu_bench/gemini-2.5-pro-preview-05-06.json -m o4-mini --disable-temperature --all
