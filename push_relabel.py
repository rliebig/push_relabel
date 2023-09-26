import pygame
import random
from pygame.locals import QUIT, KEYDOWN, K_r, K_s
import sys
import matplotlib.pyplot as plt


pygame.font.init()

GLOBAL_FONT = pygame.font.SysFont("monspace", 30)
GLOBAL_OFFSET = 493
WINDOW_HEIGHT = 1000
WINDOW_WIDTH = 1200
RIGHT_OFFSET = 80

COLOR_RED = (125, 0, 1)
COLOR_GREEN = (5, 125, 6)
COLOR_BLUE = (4, 57, 115)
COLOR_YELLOW = (128, 128, 0)
COLOR_BLACK = (0, 0, 0)
COLOR_GREY = (90, 90, 90)
COLOR_WHITE = (255, 255, 255)

LEFT_OFFSET = 100


def draw_circle_alpha(color, center, radius, alpha):
    global SCREEN
    target_rect = pygame.Rect(center, (0, 0)).inflate((radius * 2, radius * 2))
    shape_surf = pygame.Surface(target_rect.size, pygame.SRCALPHA)
    shape_surf.set_alpha(alpha)
    pygame.draw.circle(shape_surf, color, (radius, radius), radius)
    SCREEN.blit(shape_surf, target_rect)


ALGORITHM_STEPS = [
    r"\mathrm{for}\ uv\ \in\ E(G)\ \mathrm{do}",
    r"\ \ \ \ if\ u = s\ \mathrm{then}",
    r"\ \ \ \ \ \ \ \ f(sv) \leftarrow c(sv)",
    r"\ \ \ \ \mathrm{else}",
    r"\ \ \ \ \ \ \ \ f(uv) \leftarrow 0",
    r"h(s) = V",
    r"\mathrm{for}\ u\ \in\ V(G)\ \backslash\  \{s\}",
    r"\ \ \ \ h(u) = 0",
    r"\mathrm{while}\ \exists\mathrm{aktiver Knoten}\ a\ \mathrm{do}",
    r"\ \ \ \ \mathrm{if}\ \exists \mathrm{aktive\ Abw\"artskante}\ ab \in E(R_G)\ \mathrm{then}",  # noqa: E501
    r"\ \ \ \ \ \ \ \ x \leftarrow min\{\delta_{f}(a),rest_{f}(ab)\}",
    r"\ \ \ \ \ \ \ \ \mathrm{if} ab \in E(G)\ \mathrm{then}",
    r"\ \ \ \ \ \ \ \ \ \ \ \ \ f(ab) \leftarrow f(ab) + x",
    r"\ \ \ \ \ \ \ \ \mathrm{else}",
    r"\ \ \ \ \ \ \ \ \ \ \ \ \ f(ba) \leftarrow f(ba) - x",
    r"\ \ \ \ \mathrm{else}",
    r"\ \ \ \ \ \ \ \ h(a) \leftarrow h(a) + 1",
    r"\mathrm{return}",
]


def generate_initial_images():
    for line in range(len(ALGORITHM_STEPS)):
        display_algorithm(line, False)
        display_algorithm(line, True)


def display_algorithm(line=0, highlight=False):
    current_step = ALGORITHM_STEPS[line]
    print(current_step)
    filename = f"line{line}" + str("red" if highlight else "") + ".png"
    if highlight:
        render_latex(current_step, filename=filename, color="red")
    else:
        render_latex(current_step, filename=filename)


def render_latex(formula, filename, fontsize=7, dpi=300, color="black"):
    """Renders LaTeX formula into image."""
    fig = plt.figure(figsize=(0.01, 0.01))
    fig.text(0, 0, "${}$".format(formula), color=color, fontsize=fontsize)
    fig.savefig(
        filename, dpi=dpi, transparent=True, pad_inches=0.0, bbox_inches="tight"
    )
    plt.close(fig)


PRELOADED_IMAGES = {}


def preload_images():
    global LEFT_OFFSET
    for line in range(len(ALGORITHM_STEPS)):
        # not too DRY...
        name = f"line{line}red.png"
        img = pygame.image.load(name)
        PRELOADED_IMAGES[name] = img

        name = f"line{line}.png"
        img = pygame.image.load(name)
        PRELOADED_IMAGES[name] = img

        width = img.get_width()

        if width > LEFT_OFFSET:
            LEFT_OFFSET = width


def paint_algorithm(highlight_line=0):
    global SCREEN, LEFT_OFFSET, GLOBAL_OFFSET
    GLOBAL_OFFSET = 0
    for line in range(len(ALGORITHM_STEPS)):
        if line == highlight_line:
            name = f"line{line}red.png"
        else:
            name = f"line{line}.png"

        img = PRELOADED_IMAGES[name]
        GLOBAL_OFFSET += img.get_height()
        SCREEN.blit(img, (0, GLOBAL_OFFSET))


class Edge:
    def __init__(self, capacity, a, b):
        self.capacity = capacity
        self.flow = 0
        self.a = a
        self.b = b
        self.flow_modified = False

    def get_a(self):
        return self.a

    def get_b(self):
        return self.b

    def capacity(self):
        return self.capacity

    def flow(self):
        return self.flow

    def __str__(self):
        return f" {self.capacity}/{self.flow}"

    def draw(self, color=COLOR_BLUE):
        global SCREEN
        # we need to draw flow and capacity as well
        pygame.draw.aaline(
            SCREEN,
            color,
            self.a.get_coordinates(),
            self.b.get_coordinates(),
        )
        # generate a visual difference between assigned
        # flows and empty flows
        text_color = COLOR_GREY
        if self.flow_modified:
            text_color = COLOR_BLACK

        text = GLOBAL_FONT.render(f"{self.flow}/{self.capacity}", True, text_color)
        first_x = self.a.get_coordinates()[0]
        second_x = self.b.get_coordinates()[0]

        first_y = self.a.get_coordinates()[1]
        second_y = self.b.get_coordinates()[1]

        vector_c = (second_x - first_x, second_y - first_y)
        middle_of_line_x = first_x + (vector_c[0] / 2)
        middle_of_line_y = first_y + (vector_c[1] / 2)

        vector_middle_line = (middle_of_line_x, middle_of_line_y)
        SCREEN.blit(text, vector_middle_line)

    def set_flow(self, new_flow):
        self.flow_modified = True
        self.flow = new_flow


class Vertex:
    def __init__(self, x, y, is_source=False):
        self.x = x
        self.y = y
        self.start_y = self.y
        self.active = False
        self.overflow = 0
        self.is_source = is_source
        self.height = 0
        self.height_modified = False
        self.is_sink = False

    def get_coordinates(self):
        return (self.x, self.y)

    def is_active(self):
        return self.active

    def set_active(self, state):
        self.active = state

    def set_overflow(self, state):
        if not self.is_sink and not self.is_source:
            self.overflow = state

    def set_height(self, state):
        self.height = state
        self.height_modified = True
        self.y = self.start_y - (20 * self.height)

    def draw(self):
        global SCREEN
        working_y = self.y
        draw_circle_alpha(
            COLOR_RED if self.active else COLOR_GREEN,
            (self.x, working_y),
            20,
            100.0,
        )
        if self.overflow > 0:
            draw_circle_alpha(
                COLOR_WHITE,
                (self.x, working_y),
                10,
                255.0,
            )
            text = GLOBAL_FONT.render(f"{self.overflow}", True, COLOR_BLACK)
            SCREEN.blit(text, (self.x - 6, working_y - 8))
        if self.height_modified:
            text = GLOBAL_FONT.render(f"h = {self.height}", True, COLOR_BLACK)
            SCREEN.blit(text, (self.x, working_y + 12))

        # we also need to give each node a name and find a way
        # to visualize the height function...


class FlowNetwork:
    def __init__(self):
        global LEFT_OFFSET, GLOBAL_OFFSET, RIGHT_OFFSET
        self.vertices = []
        self.edges = []
        # every vertic is assigned to a layer
        # this ensure that drawing is easy
        # while vertices may connect to layers
        # much further back and forth
        # we do not want any connections on
        # the same layer for now
        self._layers = []

        # add s to our collection
        half_way_down = GLOBAL_OFFSET / 2

        initial_width_point = LEFT_OFFSET + 10
        s = Vertex(initial_width_point, half_way_down, is_source=True)
        self.vertices.append(s)
        # now add t to our collection
        t = Vertex(WINDOW_WIDTH - RIGHT_OFFSET, half_way_down)
        t.is_sink = True
        self.vertices.append(t)

        # we know add two nodes
        # therefore we have four layers
        four_split = (WINDOW_WIDTH - RIGHT_OFFSET - initial_width_point) / 3

        first_layer_x = initial_width_point + four_split
        second_layer_x = initial_width_point + (2 * four_split)

        v0 = Vertex(first_layer_x, half_way_down)
        v1 = Vertex(second_layer_x, half_way_down)

        s_to_v0 = Edge(3, s, v0)
        v0_to_v1 = Edge(2, v0, v1)
        v1_to_t = Edge(1, v1, t)

        [self.edges.append(x) for x in [s_to_v0, v0_to_v1, v1_to_t]]
        [self.vertices.append(x) for x in [v0, v1]]

    def get_active_nodes(self):
        """Get active nodes according to Goldberg-Tarjan Algorithm"""

    def prune_active_state(self):
        for vertex in self.vertices:
            vertex.active = False

    def draw(self):
        for edge in self.edges:
            edge.draw()
        for vertex in self.vertices:
            vertex.draw()

    def get_rest_network(self):
        rest_network = []
        for edge in self.edges:
            print("adding to rest netwrok")
            print(edge)
            # more trick than anticipated
            rest = edge.capacity - edge.flow
            inverted_rest = edge.flow

            rest_edge = Edge(rest, edge.b, edge.a)
            rest_edge.flow = rest
            rest_network.append(rest_edge)
            second_edge = Edge(rest, edge.a, edge.b)
            second_edge.flow = inverted_rest
            rest_network.append(second_edge)

        return rest_network

    def get_potential(self):
        current_potential = 0
        for node in self.vertices:
            if node.overflow > 0:
                current_potential += node.height

        return current_potential

    def update_overflow(self):
        for node in self.get_vertices():
            # this is technically not efficient - but it is convienent for our purposes
            ingoing = sum([edge.flow for edge in self.get_edges() if edge.b == node])
            outgoing = sum([edge.flow for edge in self.get_edges() if edge.a == node])
            node.set_overflow(ingoing - outgoing)

    # GRAPHIC RULES:
    # Es gibt nur die Quelle S und die Senke T
    # Jeder Knoten darf muss somit mindestens eine
    # eingehende und ausgehende Kante haben.
    def get_edges(self):
        return self.edges

    def get_vertices(self):
        return self.vertices


def goldberg_tarjan(flow_network, state, step_to_compute):
    # a rather painstaking exercise in splitting a procedural
    # algorithm in individual steps and then computing them...

    # this vaguely resembles a state machine.
    # DO NOT USE THIS IMPLEMENTATION FOR WHATEVER PURPOSES.
    print(state)
    # goto debugging from hell
    if step_to_compute == 0:
        # for uv in E(G) do
        if "initial_loop" in state:
            if len(state["initial_loop"]) == state["init_i"] + 1:
                return state, 5
            else:
                state["init_i"] += 1
                state["selected_edge_init"] = state["initial_loop"][state["init_i"]]
                return state, 1
        else:
            state["initial_loop"] = flow_network.get_edges()

            state["init_i"] = 0
            state["selected_edge_init"] = state["initial_loop"][state["init_i"]]
            return state, 1
    elif step_to_compute == 1:
        if state["selected_edge_init"].a.is_source:
            return state, 2
        else:
            return state, 3
    elif step_to_compute == 2:
        capacity = state["selected_edge_init"].capacity
        state["selected_edge_init"].set_flow(capacity)
        state["selected_edge_init"].b.set_overflow(capacity)
        return state, 0
    elif step_to_compute == 3:
        return state, 4
    elif step_to_compute == 4:
        # TODO
        # this step is currently not visually clear ...
        # maybe grey out capacity text or something like that ...
        state["selected_edge_init"].set_flow(0)
        return state, 0
    elif step_to_compute == 5:
        for vertex in flow_network.get_vertices():
            if vertex.is_source:
                vertex.set_height(len(flow_network.get_vertices()))
                break

        return state, 6
    elif step_to_compute == 6:
        #
        if "height_loop" in state:
            if len(state["height_loop"]) == state["init_i"] + 1:
                return state, 8
            else:
                state["init_i"] += 1
                state["height_loop_vertex"] = state["height_loop"][state["init_i"]]
                return state, 7
        else:
            # we are not trying to programm this at utmost efficiency
            # we are trying to code this as similar as possible to the original
            # implementation and faithfully represent it on screen...
            state["height_loop"] = [
                x for x in flow_network.get_vertices() if not x.is_source
            ]

            state["init_i"] = 0
            state["height_loop_vertex"] = state["height_loop"][state["init_i"]]
            return state, 7
    elif step_to_compute == 7:
        print(state["height_loop_vertex"])
        state["height_loop_vertex"].set_height(0)
        return state, 6
    elif step_to_compute == 8:
        # we can not use our "simple" loop statement here
        # because we actively have to check for an active node
        flow_network.update_overflow()
        active_nodes = [
            node for node in flow_network.get_vertices() if node.overflow > 0
        ]
        if len(active_nodes) == 0:
            return state, 18

        state["selected_node"] = random.choice(active_nodes)
        flow_network.prune_active_state()
        state["selected_node"].active = True
        return state, 9
    elif step_to_compute == 9:
        # eine Kante ist eine aktive Abwaertskante, wenn a ein
        # aktiver Knoten ist (was hier durch Schritt 8 zwangslauefig gegeben ist)
        # rest(ab) > 0 (i.e. kapazitaet steht zur Verfuegung) und
        # h(a) > h(b)
        flow_network.update_overflow()
        print([str(x) for x in flow_network.get_rest_network()])
        for edge in flow_network.get_rest_network():
            a = edge.a
            b = edge.b
            print("---a---")
            print(a.height)
            print(a.overflow)
            print("---b---")
            print(b.height)
            print(b.overflow)
            print("---flow---")
            print(edge.flow)
            if b.height > a.height and edge.flow > 0 and b.overflow > 0:
                state["active_downward_edge"] = edge
                return state, 10

        # else branch in the script...
        return state, 15
    elif step_to_compute == 10:
        edge = state["active_downward_edge"]
        delta_f_a = edge.b.overflow
        rest_f = edge.flow
        print(f"rest_f {rest_f}")
        print(f"delta_f_a {delta_f_a}")
        if rest_f >= delta_f_a:
            state["min"] = delta_f_a
        else:
            state["min"] = rest_f
        return state, 11
    elif step_to_compute == 11:
        # update our vertices.
        edge = state["active_downward_edge"]
        for comparison_edge in flow_network.get_edges():
            if edge.a == comparison_edge.a and edge.b == comparison_edge.b:
                return state, 12

        return state, 13
    elif step_to_compute == 12:
        edge = state["active_downward_edge"]
        for comparison_edge in flow_network.get_edges():
            if edge.a == comparison_edge.a and edge.b == comparison_edge.b:
                comparison_edge.set_flow(edge.flow - state["min"])
                flow_network.update_overflow()
                return state, 8

    elif step_to_compute == 13:
        return state, 14
    elif step_to_compute == 14:
        edge = state["active_downward_edge"]
        for comparison_edge in flow_network.get_edges():
            # i am not entirely sure that this work tbh
            if edge.a == comparison_edge.b and edge.b == comparison_edge.a:
                print(state["min"])
                # THIS IS WRONG
                comparison_edge.set_flow(comparison_edge.flow + state["min"])
        flow_network.update_overflow()
        return state, 8
    elif step_to_compute == 15:
        return state, 16
    elif step_to_compute == 16:
        state["selected_node"].set_height(state["selected_node"].height + 1)
        state["incremented_node"] = state["selected_node"]
        return state, 8
    else:
        flow_network.prune_active_state()
        return state, 17


def main():
    global SCREEN, CLOCK, LEFT_OFFSET, WINDOW_HEIGHT, WINDOW_WIDTH
    pygame.init()
    pygame.font.init()
    generate_initial_images()
    preload_images()
    SCREEN = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    CLOCK = pygame.time.Clock()

    flow_network = FlowNetwork()
    step = 0
    state = {}
    accumulated_potential = []

    i = 0
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_r:
                    pass
                if event.key == K_s:
                    state, step = goldberg_tarjan(flow_network, state, step)
                    pygame.image.save(SCREEN, f"{i}.png")
                    i += 1
                    accumulated_potential.append(flow_network.get_potential())
                    # add a boundary protection at some point...

            SCREEN.fill(COLOR_WHITE)
            flow_network.draw()
            paint_algorithm(highlight_line=step)

            pygame.display.update()


if __name__ == "__main__":
    main()
