-e gemini-2.0-flash -m gemini-2.5-flash-lite-preview-06-17: 1m4.168s
-e gemini-2.0-flash -m gemini-2.5-flash: 1m4.323s
-e gemini-2.0-flash -m gemini-2.5-pro: 1m6.737s
-e gemini-2.0-flash -m gemini-2.5-pro-preview-03-25: 1m6.965s
-e gemini-2.0-flash -m gemini-2.5-pro-preview-05-06: 1m4.792s
-e gemini-2.0-flash -m gemini-2.5-pro-preview-06-05: 1m4.802s

-e gemini-2.5-flash -m gemini-2.5-flash-lite-preview-06-17: 5m17.425s
-e gemini-2.5-flash -m gemini-2.5-flash: 7m43.252s
-e gemini-2.5-flash -m gemini-2.5-pro: 5m20.444s
-e gemini-2.5-flash -m gemini-2.5-pro-preview-03-25: 4m45.388s
-e gemini-2.5-flash -m gemini-2.5-pro-preview-05-06: 4m56.370s
-e gemini-2.5-flash -m gemini-2.5-pro-preview-06-05: 5m20.511s

-e gemini-2.5-flash-preview-05-20 -m gemini-2.5-flash-lite-preview-06-17: 5m21.680s
-e gemini-2.5-flash-preview-05-20 -m gemini-2.5-flash: 7m44.857s
-e gemini-2.5-flash-preview-05-20 -m gemini-2.5-pro: 5m27.564s
-e gemini-2.5-flash-preview-05-20 -m gemini-2.5-pro-preview-03-25: 4m49.430s
-e gemini-2.5-flash-preview-05-20 -m gemini-2.5-pro-preview-05-06: 4m59.420s
-e gemini-2.5-flash-preview-05-20 -m gemini-2.5-pro-preview-06-05: 5m22.622s

-e gemini-2.5-flash-lite-preview-06-17 -m gemini-2.5-flash-lite-preview-06-17: 0m50.363s
-e gemini-2.5-flash-lite-preview-06-17 -m gemini-2.5-flash: 0m54.196s
-e gemini-2.5-flash-lite-preview-06-17 -m gemini-2.5-pro: 0m48.657s
-e gemini-2.5-flash-lite-preview-06-17 -m gemini-2.5-pro-preview-03-25: 0m47.653s
-e gemini-2.5-flash-lite-preview-06-17 -m gemini-2.5-pro-preview-05-06: 0m45.225s
-e gemini-2.5-flash-lite-preview-06-17 -m gemini-2.5-pro-preview-06-05: 5m25.206s

-e gemini-2.5-pro -m gemini-2.5-flash-lite-preview-06-17: 11m50.860s
-e gemini-2.5-pro -m gemini-2.5-flash: 11m58.536s
-e gemini-2.5-pro -m gemini-2.5-pro: 12m12.061s
-e gemini-2.5-pro -m gemini-2.5-pro-preview-03-25: 13m56.954s
-e gemini-2.5-pro -m gemini-2.5-pro-preview-05-06: 11m53.872s
-e gemini-2.5-pro -m gemini-2.5-pro-preview-06-05: 14m13.949s

-e gpt-4.1-mini -m gemini-2.5-flash-lite-preview-06-17: 2m27.006s
-e gpt-4.1-mini -m gemini-2.5-flash: 3m51.298s
-e gpt-4.1-mini -m gemini-2.5-pro: 3m2.175s
-e gpt-4.1-mini -m gemini-2.5-pro-preview-03-25: 2m54.316s
-e gpt-4.1-mini -m gemini-2.5-pro-preview-05-06: 2m54.509s
-e gpt-4.1-mini -m gemini-2.5-pro-preview-06-05: 3m3.649s

-e o4-mini -m gemini-2.5-flash-lite-preview-06-17 -t -1 -st -1 -n 1: 44m0.572s
-e o4-mini -m gemini-2.5-flash -t -1 -st -1 -n 1: 36m59.537s
-e o4-mini -m gemini-2.5-pro-preview-03-25 -t -1 -st -1 -n 1: 25:52+0:15?
-e o4-mini -m gemini-2.5-pro-preview-05-06 -t -1 -st -1 -n 1: 29m52.961s
-e o4-mini -m gemini-2.5-pro-preview-06-05 -t -1 -st -1 -n 1: 29m51.839s
-e o4-mini -m gemini-2.5-pro -t -1 -st -1 -n 1: 29m29.377s

```text
$ time uv run judge_answers.py -d shaberi3 -e o4-mini -m gemini-2.5-flash-lite-preview-06-17 -t -1 -st -1 -n 1
Map:  51%|█████████████████████████████████▌                                | 61/120 [14:51<09:24,  9.57s/ examples]Backing off 0.9 seconds after 1 tries. Error: Error code: 400 - {'error': {'message': 'Invalid prompt: your prompt was flagged as potentially violating our usage policy. Please try again with a different prompt: https://platform.openai.com/docs/guides/reasoning#advice-on-prompting', 'type': 'invalid_request_error', 'param': None, 'code': 'invalid_prompt'}}
```
```text:-n 8
Backing off 0.9 seconds after 1 tries. Error: Error code: 400 - {'error': {'message': 'Invalid prompt: your prompt was flagged as potentially violating our usage policy. Please try again with a different prompt: https://platform.openai.com/docs/guides/reasoning#advice-on-prompting', 'type': 'invalid_request_error', 'param': None, 'code': 'invalid_prompt'}}
```
```sh
$ time uv run judge_answers.py -d shaberi3 -e o4-mini -m gemini-2.5-pro-preview-05-06 -t -1 -st -1 -n 1
Map:  51%|█████████████████████████████████▌                                | 61/120 [09:41<09:54, 10.07s/ examples]Backing off 0.1 seconds after 1 tries. Error: Error code: 400 - {'error': {'message': 'Invalid prompt: your prompt was flagged as potentially violating our usage policy. Please try again with a different prompt: https://platform.openai.com/docs/guides/reasoning#advice-on-prompting', 'type': 'invalid_request_error', 'param': None, 'code': 'invalid_prompt'}}
Backing off 0.7 seconds after 2 tries. Error: Error code: 400 - {'error': {'message': 'Invalid prompt: your prompt was flagged as potentially violating our usage policy. Please try again with a different prompt: https://platform.openai.com/docs/guides/reasoning#advice-on-prompting', 'type': 'invalid_request_error', 'param': None, 'code': 'invalid_prompt'}}
Map: 100%|█████████████████████████████████████████████████████████████████| 120/120 [18:05<00:00,  9.05s/ examples]
Creating json from Arrow format: 100%|████████████████████████████████████████████████| 1/1 [00:00<00:00, 71.70ba/s]
Map: 100%|█████████████████████████████████████████████████████████████████| 100/100 [06:54<00:00,  4.14s/ examples]
Creating json from Arrow format: 100%|███████████████████████████████████████████████| 1/1 [00:00<00:00, 226.19ba/s]
Map: 100%|███████████████████████████████████████████████████████████████████| 60/60 [04:36<00:00,  4.61s/ examples]
Creating json from Arrow format: 100%|███████████████████████████████████████████████| 1/1 [00:00<00:00, 375.97ba/s]

real    29m52.961s
user    0m19.566s
sys     0m0.824s
```
- 1.931M (Input 1.429M, Output 501.755K)

# old

-e gemini-2.5-flash -m gemini-2.5-pro: 5m25.841s
-e gemini-2.5-flash -m gemini-2.5-pro-preview-03-25: 4m40.162s
-e gemini-2.5-flash -m gemini-2.5-pro-preview-05-06: 4m56.105s
-e gemini-2.5-flash -m gemini-2.5-pro-preview-06-05: 5m7.895s

-e gemini-2.5-pro -m gemini-2.5-pro: 11m24.566s

-e gemini-2.5-flash-lite-preview-06-17 -m gemini-2.5-pro: 0m47.999s
-e gemini-2.5-flash-lite-preview-06-17 -m gemini-2.5-flash: 0m54.868s

-e gemini-2.0-flash -m gemini-2.5-pro: 1m6.132s
-e gemini-2.0-flash -m gemini-2.5-flash: 2m27.822s
-e gemini-2.0-flash -m gemini-2.5-flash-lite-preview-06-17: 1m33.370s

# answer

-m gemini-2.5-flash: 9m55.558s
-m gemini-2.5-flash-lite-preview-06-17: 6m14.362s
