from panda3d.core import *
from direct.showbase.DirectObject import DirectObject
from direct.actor.Actor import Actor
import direct.directbase.DirectStart
import random
from p3dopenvr.p3dopenvr import P3DOpenVR
import openvr
livedata = False

def updatePose(boat):
    MAXP = 5
    MINP = -5
    MAXR = 10
    MINR = -10

    if(livedata):
        print(boat.getH())
        print(boat.getP())
        print(boat.getR())
    else:
        if boat.pport:
            if boat.getP()<0:
                boat.setP(boat.getP()+(1-(boat.getP()/MINP))/12)
            elif boat.getP()<MAXP-0.5:
                boat.setP(boat.getP()+(1-(boat.getP()/MAXP))/12)
            if boat.getP() >= MAXP-0.5:
                boat.pport = False
        else:
            if boat.getP()>0:
                boat.setP(boat.getP()-(1-(boat.getP()/MAXP))/12)
            elif boat.getP()>MINP+0.5:
                boat.setP(boat.getP()-(1-(boat.getP()/MINP))/12)
            if boat.getP() <= MINP+0.5:
                boat.pport = True

        if boat.rbow:
            if boat.getR()<0:
                boat.setR(boat.getR()+(1-(boat.getR()/MINR))/5)
            elif boat.getR()<MAXR-1:
                boat.setR(boat.getR()+(1-(boat.getR()/MAXR))/5)
            if boat.getR() >= MAXR-1:
                boat.rbow = False
        else:
            if boat.getR()>0:
                boat.setR(boat.getR()-(1-(boat.getR()/MAXR))/5)
            elif boat.getR()>MINR+1:
                boat.setR(boat.getR()-(1-(boat.getR()/MINR))/5)
            if boat.getR() <= MINR+1:
                boat.rbow = True

class VrappOpenVR(P3DOpenVR):
    classes_map = { openvr.TrackedDeviceClass_Invalid: 'Invalid',
                    openvr.TrackedDeviceClass_HMD: 'HMD',
                    openvr.TrackedDeviceClass_Controller: 'Controller',
                    openvr.TrackedDeviceClass_GenericTracker: 'Generic tracker',
                    openvr.TrackedDeviceClass_TrackingReference: 'Tracking reference',
                    openvr.TrackedDeviceClass_DisplayRedirect: 'Display redirect',
                  }

    roles_map = { openvr.TrackedControllerRole_Invalid: 'Invalid',
                  openvr.TrackedControllerRole_LeftHand: 'Left',
                  openvr.TrackedControllerRole_RightHand: 'Right',
                  openvr.TrackedControllerRole_OptOut: 'Opt out',
                  openvr.TrackedControllerRole_Treadmill: 'Treadmill',
                }

    buttons_map = { openvr.k_EButton_System: 'System',
                    openvr.k_EButton_ApplicationMenu: 'Application Menu',
                    openvr.k_EButton_Grip: 'Grip',
                    openvr.k_EButton_DPad_Left: 'Pad left',
                    openvr.k_EButton_DPad_Up: 'Pad up',
                    openvr.k_EButton_DPad_Right: 'Pad right',
                    openvr.k_EButton_DPad_Down: 'Pad down',
                    openvr.k_EButton_A: 'A',
                    openvr.k_EButton_ProximitySensor: 'Proximity sensor',
                    openvr.k_EButton_Axis0: 'Axis 0',
                    openvr.k_EButton_Axis1: 'Axis 1',
                    openvr.k_EButton_Axis2: 'Axis 2',
                    openvr.k_EButton_Axis3: 'Axis 3',
                    openvr.k_EButton_Axis4: 'Axis 4',
                    #openvr.k_EButton_SteamVR_Touchpad: 'Touchpad',
                    #openvr.k_EButton_SteamVR_Trigger: 'Trigger',
                    #openvr.k_EButton_Dashboard_Back: 'Dashboard back',
                    #openvr.k_EButton_IndexController_A: 'Controller A',
                    #openvr.k_EButton_IndexController_B: 'Controller B',
                    #openvr.k_EButton_IndexController_JoyStick: 'Controller joystick',
                  }

    button_events_map = { openvr.VREvent_ButtonPress: 'Press',
                          openvr.VREvent_ButtonUnpress: 'Unpress',
                          openvr.VREvent_ButtonTouch: 'Touch',
                          openvr.VREvent_ButtonUntouch: 'Untouch'
                        }

    def button_event(self, event):
        device_index = event.trackedDeviceIndex
        device_class = self.vr_system.getTrackedDeviceClass(device_index)
        if device_class != openvr.TrackedDeviceClass_Controller:
            return
        button_id = event.data.controller.button
        button_name = self.buttons_map.get(button_id)
        if button_name is None:
            button_name = 'Unknown button ({})'.format(button_id)
        role = self.vr_system.getControllerRoleForTrackedDeviceIndex(device_index)
        role_name = self.roles_map.get(role)
        if role_name is None:
            role_name = 'Unknown role ({})'.format(role)
        event_name = self.button_events_map.get(event.eventType)
        if event_name is None:
            event_name = 'Unknown event ({})'.format(event.eventType)
        print(role_name, button_name, event_name)

    def device_event(self, event, action):
        device_index = event.trackedDeviceIndex
        device_class = self.vr_system.getTrackedDeviceClass(device_index)
        class_name = self.classes_map.get(device_class)
        if class_name is None:
            class_name = 'Unknown class ({})'.format(class_name)
        print('Device {} {} ({})'.format(event.trackedDeviceIndex, action, class_name))

    def process_vr_event(self, event):
        if event.eventType == openvr.VREvent_TrackedDeviceActivated:
            self.device_event(event, 'attached')
        if event.eventType == openvr.VREvent_TrackedDeviceDeactivated:
            self.device_event(event, 'deactivated')
        elif event.eventType == openvr.VREvent_TrackedDeviceUpdated:
            self.device_event(event, 'updated')
        elif event.eventType in (openvr.VREvent_ButtonPress,
                                 openvr.VREvent_ButtonUnpress,
                                 openvr.VREvent_ButtonTouch,
                                 openvr.VREvent_ButtonUntouch):
            self.button_event(event)

    def new_tracked_device(self, device_index, device_anchor):
        print("Adding new device", device_anchor.name)
        device_class = self.vr_system.getTrackedDeviceClass(device_index)
        if device_class == openvr.TrackedDeviceClass_Controller:
            model = loader.loadModel("box")
            model.reparent_to(device_anchor)
            model.set_scale(0.1)
        else:
            print(device_class)
            model = loader.loadModel("camera")
            model.reparent_to(device_anchor)
            model.set_scale(0.1)


class World(DirectObject):
    def toggleView(self):
        if self.fpView:
            self.fpView = False
            base.camera.setPosHpr(-50,-50,20,-47,-10,0)
            base.camera.wrtReparentTo(render)
#            base.enableMouse()
        else:
            base.disableMouse()
            self.fpView = True
            self.pivotNode.setPosHpr(0,0,-2,0,0,0)
            self.boat.setHpr(0,0,0)
            base.camera.setPosHpr(0,0,3.2,0,0,0)
            base.camera.wrtReparentTo(self.pivotNode)
    def __init__(self):
        self.fpView = False
        self.cloud_root=render.attachNewNode('cloudRoot')
        cloud_lod = FadeLODNode('cloud_lod')
        cloud = NodePath(cloud_lod)
        lod0 = loader.loadModel("res/cloud")
        lod0.reparentTo(cloud)
        cloud_lod.addSwitch(1000, 0)
        shader = loader.loadShader("res/clouds.cg")
        cloud_lod.setFadeTime(5.0)
        self.sky=loader.loadModel("res/sky")
        self.sky.reparentTo(self.cloud_root)
        self.sky.setBin('background', 1)
        self.sky.setDepthWrite(0)
        self.sky.setLightOff()
        self.sky.setScale(100)
        self.sun=loader.loadModel("res/sun")
        self.sun.reparentTo(self.cloud_root)
        self.sun.setBin('background', 1)
        self.sun.setDepthWrite(0)
        self.sun.setLightOff()
        self.sun.setScale(100)
        self.sun.setP(20)
        #config here!
        self.cloud_x=2000
        self.cloud_y=2000
        self.cloud_z=100
        self.cloud_speed=0.3
        cloud_size=20
        cloud_count=20
        cloud_color=(0.6,0.6,0.7, 1.0)
        self.clouds=[]
        for i in range(cloud_count):
            self.clouds.append(cloud.copyTo(self.cloud_root))
            self.clouds[-1].getChild(0).getChild(0).setScale(cloud_size+random.random(),cloud_size+random.random(),cloud_size+random.random())
            self.clouds[-1].setPos(render,random.randrange(-self.cloud_x/2, self.cloud_x/2),random.randrange(-self.cloud_y/2,self.cloud_y/2), random.randrange(self.cloud_z)+self.cloud_z)            
            self.clouds[-1].setShaderInput("offset", Vec4(random.randrange(5)*0.25, random.randrange(9)*0.125, 0, 0))
            self.clouds[-1].setShader(shader)
            self.clouds[-1].setBillboardPointEye()
            self.clouds[-1].setColor(cloud_color)
            self.clouds[-1].setDepthWrite(0)
            self.clouds[-1].setDepthTest(0)
            #self.clouds[-1].setBin("fixed", 0)
            self.clouds[-1].setBin('background', 1)
        self.cloud_root.setColor(cloud_color)
        self.sky.setColor(1,1,1,1)
        self.sun.setColor(1,1,1,1)
        self.time=0
        self.uv=Vec4(0, 0, 0.25, 0)
        render.setShaderInput("time", self.time)
        render.setShaderInput("uv", self.uv)
        taskMgr.add(self.update,"updateTask")
        ################
        #water
        ################
        #Create the plane geometry and add it to the scene
        maker = CardMaker("grid")
        maker.setFrame( 0, 2000, 0, 2000)
        self.waterNP = NodePath('waterSurface')
        node = self.waterNP.attachNewNode(maker.generate())
        node.setHpr(0,-90,0)
        node.setPos(-1000, -1000, 0)
        #node.setScale(200)
        self.waterNP.reparentTo(render)
        self.waterNP.setLightOff(1)
        #Add a buffer and camera that will render the reflection texture
        wBuffer = base.win.makeTextureBuffer("water", 512, 512)
        wBuffer.setClearColorActive(True)
        wBuffer.setClearColor(base.win.getClearColor())
        self.wCamera = base.makeCamera(wBuffer)
        self.wCamera.reparentTo(render)
        self.wCamera.node().setLens(base.camLens)
        self.wCamera.node().setCameraMask(BitMask32.bit(1))

        self.waterNP.hide(BitMask32.bit(1))
        #Create this texture and apply settings
        wTexture = wBuffer.getTexture()
        wTexture.setWrapU(Texture.WMClamp)
        wTexture.setWrapV(Texture.WMClamp)
        wTexture.setMinfilter(Texture.FTLinearMipmapLinear)
        #Create plane for clipping and for reflection matrix
        self.wPlane = Plane(Vec3(0, 0, 1), Point3(0, 0, self.waterNP.getZ()))
        wPlaneNP = render.attachNewNode(PlaneNode("water", self.wPlane))
        tmpNP = NodePath("StateInitializer")
        tmpNP.setClipPlane(wPlaneNP)
        tmpNP.setAttrib(CullFaceAttrib.makeReverse())
        self.wCamera.node().setInitialState(tmpNP.getState())
        self.waterNP.projectTexture(TextureStage("reflection"), wTexture, self.wCamera)

        self.waterNP.setShader(loader.loadShader("res/water2.cg"))
        self.waterNP.setShaderInput("water_norm", loader.loadTexture('res/water-normal.jpg'))
        self.waterNP.setShaderInput("water_alpha", loader.loadTexture('res/water_alpha.png'))
        self.waterNP.setTransparency(TransparencyAttrib.MDual)
        self.offset=0.0
        #light
        dlight = DirectionalLight('dlight')
        dlight.setColor(VBase4(1, 1, 0.5, 1))
        dlnp = render.attachNewNode(dlight)
        dlnp.setHpr(0, 180+20, 0)
        render.setShaderInput("dlight0", dlnp)
        render.setLight(dlnp)
        self.boat = Actor("res/boat.bam")
        #self.boat = loader.loadModel("res/boat.obj")
        self.boat.setZ(-2)
        self.boat.setScale(0.01)
        self.boat.pport = True
        self.boat.rbow = True
        self.boat.reparentTo(render)
        self.boat.setHpr(0,0,0)
        self.pivotNode = render.attachNewNode("environ-pivot")
        self.pivotNode.setPosHpr(0,0,-2,0,0,0) # Set location of pivot point
        #base.camera.wrtReparentTo(self.pivotNode)
        self.accept("space", self.toggleView)
        self.toggleView()
        self.toggleView()
        self.vr = VrappOpenVR()
        self.vr.init()

    def update(self, task):
        #print(base.camera.getY())
        updatePose(self.boat)
        self.pivotNode.setHpr(self.boat.getH(),self.boat.getP(),self.boat.getR())
        self.time+=task.time*self.cloud_speed
        self.offset+=task.time
        #water
        self.wCamera.setMat(base.cam.getMat(render)*self.wPlane.getReflectionMat())
        render.setShaderInput("offset", self.offset)
        #clouds
        self.cloud_root.setPos(base.camera.getPos(render))
        for model in self.clouds:
            model.setY(model, -task.time*10.0)
            if model.getY(self.cloud_root) <-self.cloud_y/2:
                model.setY(self.cloud_root,self.cloud_y/2)
        if self.time>1.0:
            self.cloud_speed*=-1.0
            self.uv[0]+=0.5
            if self.uv[0]>1.0:
                self.uv[0]=0
                self.uv[1]+=0.125
                #if self.uv[1]>1.0:
                #    self.uv=Vec4(0, 0, 0, 0)
        if self.time<0.0:
            self.cloud_speed*=-1.0
            self.uv[2]+=0.5
            if self.uv[2]>1.0:
                self.uv[2]=0.25
                self.uv[3]+=0.125
                #if self.uv[3]>1.0:
                #    self.uv=Vec4(0, 0, 0, 0)
        render.setShaderInput("time", self.time)
        render.setShaderInput("uv", self.uv)
        return task.again

w = World()
base.disableMouse()
#base.oobe()
#base.camera.setPosHpr(0,-50,5,0,0,0)
base.run()
