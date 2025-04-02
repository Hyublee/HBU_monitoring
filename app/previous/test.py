import time
import random

target_delay = 10 # ms

while True:
    start_time = time.time()
    delay = random.randint(1, 15)
    time.sleep(delay/1000)
    print(f"loop delay time: {delay}ms")
    loop_time = time.time() - start_time

    wait_time = target_delay - loop_time
    # wait time이 양수일때 여유시간 존재 (10ms - 8ms일 경우 여유시간 +2ms)
    # wait time이 음수일때 지연 발생 (10ms - 15ms일 경우 지연시간 -5ms) -> 2 loop cycle에 맞춰서 보상..
    print(f"wait time: {wait_time} ms")
    if wait_time >= 0:
        time.sleep(wait_time)

    else:
        
