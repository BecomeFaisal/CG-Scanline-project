import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
                             QPushButton, QSlider, QCheckBox, QLabel, QGroupBox)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QOpenGLWidget
from OpenGL.GL import *
from OpenGL.GLU import *

# -----------------------
# OpenGL Widget
# -----------------------
class GLWidget(QOpenGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.rot_x, self.rot_y = 20, -30
        self.last_x, self.last_y = 0, 0
        self.is_dragging = False

        # Scanlines
        self.scanlines = [2.5, 1.5, 0.5]
        self.scan_speed = 0.02
        self.animation_running = True
        self.opaque_mode = False  # fully solid objects

        # Shapes
        self.shapes = [
            {"type": "cube", "color": (0.3,0.5,0.9,0.7), "visible": True, "pos": [0,0,-6], "size": 2, "rot": 0},
            {"type": "pyramid", "color": (0.9,0.6,0.3,0.7), "visible": True, "pos": [-2,0,-5], "size": 2, "rot": 0},
            {"type": "prism", "color": (0.6,0.3,0.9,0.7), "visible": True, "pos": [2,0,-4], "size": 1.5, "rot": 0},
        ]

    def initializeGL(self):
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glLightfv(GL_LIGHT0, GL_POSITION, (5,5,10,1))
        glLightfv(GL_LIGHT0, GL_AMBIENT, (0.3,0.3,0.3,1))
        glLightfv(GL_LIGHT0, GL_DIFFUSE, (0.7,0.7,0.7,1))
        glLightfv(GL_LIGHT0, GL_SPECULAR, (0.3,0.3,0.3,1))
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        glClearColor(0.85,0.9,0.95,1)

    def resizeGL(self, w, h):
        glViewport(0,0,w,h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(60, w/h if h>0 else 1, 0.1, 50)
        glMatrixMode(GL_MODELVIEW)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        gluLookAt(0,1.5,6, 0,1,-5, 0,1,0)
        glRotatef(self.rot_x,1,0,0)
        glRotatef(self.rot_y,0,1,0)

        # Draw shapes
        for shape in self.shapes:
            if shape["visible"]:
                self.draw_shape(shape)

        # Draw scanlines on top
        if not self.opaque_mode:  # skip scanlines in opaque mode if desired
            for y in self.scanlines:
                self.draw_scanline(y)

    # -----------------------
    # Shapes
    # -----------------------
    def draw_shape(self, shape):
        glPushMatrix()
        glTranslatef(*shape["pos"])
        glRotatef(shape["rot"],0,1,0)
        shape["rot"] += 0.2  # subtle rotation

        if shape["type"]=="cube": self.draw_cube(shape["size"], shape["color"])
        elif shape["type"]=="pyramid": self.draw_pyramid(shape["size"], shape["color"])
        elif shape["type"]=="prism": self.draw_prism(shape["size"], shape["color"])
        glPopMatrix()

    def draw_cube(self,s,color):
        s/=2
        vertices=[[-s,-s,-s],[s,-s,-s],[s,s,-s],[-s,s,-s],[ -s,-s,s],[s,-s,s],[s,s,s],[-s,s,s]]
        faces=[[0,1,2,3],[4,5,6,7],[0,1,5,4],[2,3,7,6],[0,3,7,4],[1,2,6,5]]

        alpha = 1.0 if self.opaque_mode else color[3]
        glColor4f(color[0], color[1], color[2], alpha)

        for f in faces:
            glBegin(GL_POLYGON)
            for v in f:
                vx,vy,vz = vertices[v]
                glVertex3f(vx,vy,vz)
            glEnd()

        glColor3f(0,0,0)
        for f in faces:
            glBegin(GL_LINE_LOOP)
            for v in f:
                vx,vy,vz = vertices[v]
                glVertex3f(vx,vy,vz)
            glEnd()

    def draw_pyramid(self,s,color):
        s/=2
        vertices=[[-s,-s,s],[s,-s,s],[s,-s,-s],[-s,-s,-s],[0,s,0]]
        faces=[[0,1,4],[1,2,4],[2,3,4],[3,0,4],[0,1,2,3]]

        alpha = 1.0 if self.opaque_mode else color[3]
        glColor4f(color[0], color[1], color[2], alpha)

        for f in faces:
            glBegin(GL_POLYGON)
            for v in f:
                vx,vy,vz = vertices[v]
                glVertex3f(vx,vy,vz)
            glEnd()

        glColor3f(0,0,0)
        for f in faces:
            glBegin(GL_LINE_LOOP)
            for v in f:
                vx,vy,vz = vertices[v]
                glVertex3f(vx,vy,vz)
            glEnd()

    def draw_prism(self,s,color):
        s/=2
        vertices=[[-s,-s,s],[s,-s,s],[0,s,s],[-s,-s,-s],[s,-s,-s],[0,s,-s]]
        faces=[[0,1,2],[3,4,5],[0,1,4,3],[1,2,5,4],[2,0,3,5]]

        alpha = 1.0 if self.opaque_mode else color[3]
        glColor4f(color[0], color[1], color[2], alpha)

        for f in faces:
            glBegin(GL_POLYGON)
            for v in f:
                vx,vy,vz = vertices[v]
                glVertex3f(vx,vy,vz)
            glEnd()

        glColor3f(0,0,0)
        for f in faces:
            glBegin(GL_LINE_LOOP)
            for v in f:
                vx,vy,vz = vertices[v]
                glVertex3f(vx,vy,vz)
            glEnd()

    # -----------------------
    # Scanline
    # -----------------------
    def draw_scanline(self,y):
        glDisable(GL_LIGHTING)
        glBegin(GL_QUADS)
        glColor4f(0.3,1.0,0.3,0.3)
        glVertex3f(-3,y-0.05,-7)
        glVertex3f(3,y-0.05,-7)
        glVertex3f(3,y+0.05,-3)
        glVertex3f(-3,y+0.05,-3)
        glEnd()
        glEnable(GL_LIGHTING)

    # -----------------------
    # Mouse Interaction
    # -----------------------
    def mousePressEvent(self,event):
        if event.button()==Qt.LeftButton:
            self.is_dragging=True
            self.last_x = event.x()
            self.last_y = event.y()

    def mouseMoveEvent(self,event):
        if self.is_dragging:
            dx = event.x()-self.last_x
            dy = event.y()-self.last_y
            self.rot_x+=dy*0.5
            self.rot_y+=dx*0.5
            self.last_x=event.x()
            self.last_y=event.y()
            self.update()

    def mouseReleaseEvent(self,event):
        self.is_dragging=False

    # -----------------------
    # Update Scanlines
    # -----------------------
    def update_scanlines(self):
        if self.animation_running:
            for i in range(len(self.scanlines)):
                self.scanlines[i] -= self.scan_speed
                if self.scanlines[i] < -0.5:
                    self.scanlines[i] = 2.5
            self.update()

    def reset_rotation(self):
        self.rot_x, self.rot_y = 20, -30
        self.update()
# -----------------------
# Main Window
# -----------------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("3D Scanline Simulator - Opaque Mode")
        self.setGeometry(50,50,1300,850)

        self.glWidget = GLWidget(self)

        # Shapes group
        shape_group = QGroupBox("Shapes Visibility")
        self.check_cube = QCheckBox("Cube"); self.check_cube.setChecked(True)
        self.check_cube.stateChanged.connect(lambda: self.toggle_shape(0,self.check_cube))
        self.check_pyramid = QCheckBox("Pyramid"); self.check_pyramid.setChecked(True)
        self.check_pyramid.stateChanged.connect(lambda: self.toggle_shape(1,self.check_pyramid))
        self.check_prism = QCheckBox("Prism"); self.check_prism.setChecked(True)
        self.check_prism.stateChanged.connect(lambda: self.toggle_shape(2,self.check_prism))
        self.check_all = QCheckBox("All Shapes"); self.check_all.setChecked(True)
        self.check_all.stateChanged.connect(self.toggle_all_shapes)
        shape_layout = QVBoxLayout()
        for w in [self.check_cube,self.check_pyramid,self.check_prism,self.check_all]:
            shape_layout.addWidget(w)
        shape_group.setLayout(shape_layout)

        # Animation group
        anim_group = QGroupBox("Animation Controls")
        self.start_btn = QPushButton("Start/Pause")
        self.start_btn.clicked.connect(self.toggle_animation)
        self.reset_btn = QPushButton("Reset Scanlines")
        self.reset_btn.clicked.connect(self.reset_scanlines)
        self.reset_rot_btn = QPushButton("Reset Rotation")
        self.reset_rot_btn.clicked.connect(self.glWidget.reset_rotation)
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setMinimum(1); self.speed_slider.setMaximum(100); self.speed_slider.setValue(20)
        self.speed_slider.valueChanged.connect(self.change_speed)
        speed_label = QLabel("Scanline Speed")
        self.opaque_checkbox = QCheckBox("Opaque Objects")
        self.opaque_checkbox.stateChanged.connect(self.toggle_opaque_mode)
        anim_layout = QVBoxLayout()
        for w in [self.start_btn,self.reset_btn,self.reset_rot_btn,speed_label,self.speed_slider,self.opaque_checkbox]:
            anim_layout.addWidget(w)
        anim_group.setLayout(anim_layout)

        # Controls layout
        controls_layout = QVBoxLayout()
        controls_layout.addWidget(shape_group)
        controls_layout.addWidget(anim_group)
        controls_layout.addStretch()
        controls_widget = QWidget()
        controls_widget.setLayout(controls_layout)

        # Main layout
        main_layout = QHBoxLayout()
        main_layout.addWidget(self.glWidget,4)
        main_layout.addWidget(controls_widget,1)
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.glWidget.update_scanlines)
        self.timer.start(15)

    # -----------------------
    # Control Functions
    # -----------------------
    def toggle_animation(self):
        self.glWidget.animation_running = not self.glWidget.animation_running

    def reset_scanlines(self):
        self.glWidget.scanlines = [2.5,1.5,0.5]
        self.glWidget.animation_running=True

    def change_speed(self):
        self.glWidget.scan_speed = self.speed_slider.value()*0.001

    def toggle_shape(self,index,checkbox):
        self.glWidget.shapes[index]["visible"] = checkbox.isChecked()
        self.check_all.setChecked(all([s["visible"] for s in self.glWidget.shapes]))

    def toggle_all_shapes(self,state):
        visible = (state == Qt.Checked)
        for i, s in enumerate(self.glWidget.shapes):
            s["visible"]=visible
        self.check_cube.setChecked(visible)
        self.check_pyramid.setChecked(visible)
        self.check_prism.setChecked(visible)

    def toggle_opaque_mode(self,state):
        self.glWidget.opaque_mode = (state == Qt.Checked)

# -----------------------
# Run Application
# -----------------------
if __name__=="__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
