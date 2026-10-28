from pico2d import load_image, get_time, clamp, SDL_KEYDOWN, SDL_KEYUP, SDLK_SPACE, SDLK_LEFT, SDLK_RIGHT
from transitions import Machine


class Idle:
    def __init__(self, boy):
        self.boy = boy

    def enter(self):
        pass

    def exit(self):
        pass

    def do(self):
        pass

    def draw(self):
        pass


class Boy:
    states = ['IDLE', 'SLEEP', 'RUN']
    transitions = [
        {'trigger': 'time_out', 'source': 'IDLE', 'dest': 'SLEEP'},
        {'trigger': 'space_down', 'source': 'SLEEP', 'dest': 'IDLE'},
        {'trigger': 'run', 'source': ['IDLE', 'SLEEP'], 'dest': 'RUN'},
        {'trigger': 'stop', 'source': 'RUN', 'dest': 'IDLE'},
    ]

    def __init__(self):
        self.x, self.y = 400, 90
        self.frame = 0
        self.face_dir = 1
        self.dir = 0
        self.left_pressed, self.right_pressed = False, False
        self.image = load_image('animation_sheet.png')
        self.machine = Machine(model=self, states=Boy.states, transitions=Boy.transitions,
                               initial='IDLE', ignore_invalid_triggers=True)
        self.idle_start_time = get_time()

    def on_enter_IDLE(self):
        self.idle_start_time = get_time()

    def handle_event(self, event):
        if event.type == SDL_KEYDOWN and event.key == SDLK_SPACE:
            self.space_down()
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
        self.frame = (self.frame + 1) % 8
        if self.state == 'IDLE' and get_time() - self.idle_start_time > 5:
            self.time_out()
        elif self.state == 'RUN':
            self.x = clamp(25, self.x + self.dir * 5, 800 - 25)

    def draw(self):
        if self.state == 'IDLE':
            if self.face_dir == 1:
                self.image.clip_draw(self.frame * 100, 300, 100, 100, self.x, self.y)
            else:
                self.image.clip_draw(self.frame * 100, 200, 100, 100, self.x, self.y)
        elif self.state == 'SLEEP':
            # 바닥에 누운 모습: idle 이미지를 90도 회전해서 그림
            if self.face_dir == 1:
                self.image.clip_composite_draw(self.frame * 100, 300, 100, 100,
                                               3.141592 / 2, '', self.x - 25, self.y - 25, 100, 100)
            else:
                self.image.clip_composite_draw(self.frame * 100, 200, 100, 100,
                                               -3.141592 / 2, '', self.x + 25, self.y - 25, 100, 100)
        elif self.state == 'RUN':
            if self.face_dir == 1:
                self.image.clip_draw(self.frame * 100, 100, 100, 100, self.x, self.y)
            else:
                self.image.clip_draw(self.frame * 100, 0, 100, 100, self.x, self.y)
