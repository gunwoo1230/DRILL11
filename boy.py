from pico2d import load_image, get_time, clamp, SDL_KEYDOWN, SDL_KEYUP, SDLK_SPACE, SDLK_LEFT, SDLK_RIGHT, SDLK_a
from transitions import Machine

RUN_SPEED = 5
AUTO_RUN_SPEED = 15
AUTO_RUN_SCALE = 2


class Idle:
    def __init__(self, boy):
        self.boy = boy

    def enter(self):
        self.start_time = get_time()

    def exit(self):
        pass

    def do(self):
        self.boy.frame = (self.boy.frame + 1) % 8
        if get_time() - self.start_time > 5:
            self.boy.time_out()

    def draw(self):
        boy = self.boy
        if boy.face_dir == 1:
            boy.image.clip_draw(boy.frame * 100, 300, 100, 100, boy.x, boy.y)
        else:
            boy.image.clip_draw(boy.frame * 100, 200, 100, 100, boy.x, boy.y)


class Sleep:
    def __init__(self, boy):
        self.boy = boy

    def enter(self):
        pass

    def exit(self):
        pass

    def do(self):
        self.boy.frame = (self.boy.frame + 1) % 8

    def draw(self):
        boy = self.boy
        # 바닥에 누운 모습: idle 이미지를 90도 회전해서 그림
        if boy.face_dir == 1:
            boy.image.clip_composite_draw(boy.frame * 100, 300, 100, 100,
                                          3.141592 / 2, '', boy.x - 25, boy.y - 25, 100, 100)
        else:
            boy.image.clip_composite_draw(boy.frame * 100, 200, 100, 100,
                                          -3.141592 / 2, '', boy.x + 25, boy.y - 25, 100, 100)


class Run:
    def __init__(self, boy):
        self.boy = boy

    def enter(self):
        pass

    def exit(self):
        pass

    def do(self):
        boy = self.boy
        boy.frame = (boy.frame + 1) % 8
        boy.x = clamp(25, boy.x + boy.dir * RUN_SPEED, 800 - 25)

    def draw(self):
        boy = self.boy
        if boy.face_dir == 1:
            boy.image.clip_draw(boy.frame * 100, 100, 100, 100, boy.x, boy.y)
        else:
            boy.image.clip_draw(boy.frame * 100, 0, 100, 100, boy.x, boy.y)


class AutoRun:
    def __init__(self, boy):
        self.boy = boy

    def enter(self):
        # 바라보는 방향으로 자동 이동 시작
        self.boy.dir = self.boy.face_dir

    def exit(self):
        pass

    def do(self):
        boy = self.boy
        boy.frame = (boy.frame + 1) % 8
        boy.x += boy.dir * AUTO_RUN_SPEED
        # 커진 크기 기준으로 화면 끝 경계 계산
        margin = 25 * AUTO_RUN_SCALE
        if boy.x > 800 - margin:
            boy.x = 800 - margin
            boy.dir = boy.face_dir = -1
        elif boy.x < margin:
            boy.x = margin
            boy.dir = boy.face_dir = 1

    def draw(self):
        boy = self.boy
        size = 100 * AUTO_RUN_SCALE
        # 커진 만큼 위로 올려서 발이 땅에 닿도록 함
        y = boy.y + (size - 100) // 2
        if boy.face_dir == 1:
            boy.image.clip_draw(boy.frame * 100, 100, 100, 100, boy.x, y, size, size)
        else:
            boy.image.clip_draw(boy.frame * 100, 0, 100, 100, boy.x, y, size, size)


class Boy:
    states = ['IDLE', 'SLEEP', 'RUN', 'AUTO_RUN']
    transitions = [
        {'trigger': 'time_out', 'source': 'IDLE', 'dest': 'SLEEP'},
        {'trigger': 'space_down', 'source': 'SLEEP', 'dest': 'IDLE'},
        {'trigger': 'run', 'source': ['IDLE', 'SLEEP'], 'dest': 'RUN'},
        {'trigger': 'stop', 'source': 'RUN', 'dest': 'IDLE'},
        {'trigger': 'a_down', 'source': 'IDLE', 'dest': 'AUTO_RUN'},
    ]

    def __init__(self):
        self.x, self.y = 400, 90
        self.frame = 0
        self.face_dir = 1
        self.dir = 0
        self.left_pressed, self.right_pressed = False, False
        self.image = load_image('animation_sheet.png')
        self.idle_state = Idle(self)
        self.sleep_state = Sleep(self)
        self.run_state = Run(self)
        self.auto_run_state = AutoRun(self)
        self.state_objects = {
            'IDLE': self.idle_state,
            'SLEEP': self.sleep_state,
            'RUN': self.run_state,
            'AUTO_RUN': self.auto_run_state,
        }
        # 상태 전이 시 상태 객체의 enter/exit 이 자동으로 호출되도록 연결
        states = [{'name': name,
                   'on_enter': self.state_objects[name].enter,
                   'on_exit': self.state_objects[name].exit} for name in Boy.states]
        self.machine = Machine(model=self, states=states, transitions=Boy.transitions,
                               initial='IDLE', ignore_invalid_triggers=True)
        # 초기 상태는 on_enter 가 호출되지 않으므로 직접 호출
        self.idle_state.enter()

    def handle_event(self, event):
        if event.type == SDL_KEYDOWN and event.key == SDLK_SPACE:
            self.space_down()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_a:
            self.a_down()
        elif event.type in (SDL_KEYDOWN, SDL_KEYUP) and event.key in (SDLK_LEFT, SDLK_RIGHT):
            pressed = event.type == SDL_KEYDOWN
            if event.key == SDLK_LEFT:
                self.left_pressed = pressed
            else:
                self.right_pressed = pressed
            self.dir = self.right_pressed - self.left_pressed
            if self.dir != 0:
                self.face_dir = self.dir
                self.run()
            else:
                self.stop()

    def update(self):
        self.state_objects[self.state].do()

    def draw(self):
        self.state_objects[self.state].draw()
