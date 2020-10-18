from panda3d.core import *
from direct.showbase.DirectObject import DirectObject
from direct.actor.Actor import Actor
import direct.directbase.DirectStart
import random


class World(DirectObject):
    def __init__(self):
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
        self.pandaActor = Actor("res/boat.obj")
        self.pandaActor.setZ(-2)
        self.pandaActor.setScale(0.01)
        self.pandaActor.reparentTo(render)
        #self.pandaActor.loop("walk")
        base.camera.setPosHpr(15,-70,15,10,-7.42,0)

    def update(self, task):
#       base.camera.setPosHpr(15,-70,15,10,-7.42,0)
        self.time+=task.time*self.cloud_speed
        self.offset+=task.time
#       print('X'+str(self.wCamera.getX())+'Y'+str(self.wCamera.getY())+'Z'+str(self.wCamera.getX()))
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
#base.disableMouse()
base.oobe()
base.run()
