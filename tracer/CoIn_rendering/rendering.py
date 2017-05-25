import pivy.coin as coin
SOGUI_BINDING="SoQt"
from pivy.sogui import *

import numpy as N
import sys

class Renderer():
	'''	__________________________________________________________________________________________________
	Rendering:

	Renders the scene. Offers the option to highlight specific rays according to the number of times they have been 	reflected.

Reference:
[1] The inventor Mentor, Josie Wernecke (https://webdocs.cs.ualberta.ca/~graphics/books/mentor.pdf)	__________________________________________________________________________________________________

	'''
	def __init__(self, sim):
		self.sim = sim

		# Scene axis label
		length = 1
		self.r = coin.SoSeparator()
		st = coin.SoDrawStyle()
		st.lineWidth=3
		self.r.addChild(st)
		data = {'x':(1,0,0), 'y':(0,1,0), 'z':(0,0,1)}


		for k in data:

			vx,vy,vz = data[k]
			vec = (length*vx, length*vy, length*vz)		

			s1 = coin.SoSeparator()
			la = coin.SoLabel()
			la.label = k
			s1.addChild(la)
			tr1 = coin.SoTranslation()
			tr1.translation = vec
			s1.addChild(tr1)
			self.r.addChild(s1)		

			s2 = coin.SoSeparator()
			tr2 = coin.SoTransform()
			tr2.translation.setValue(data[k])
			s2.addChild(tr2)
			matxt = coin.SoMaterial()
			matxt.diffuseColor = data[k]
			s2.addChild(matxt)
			txaxis = coin.SoText2()	  
			txaxis.string = k	   
			s2.addChild(txaxis)
			self.r.addChild(s2)

			ma = coin.SoMaterial()
			ma.diffuseColor = data[k]
			self.r.addChild(ma)

			co = coin.SoCoordinate3()
			co.point.setValues(0,2,[(0,0,0),vec])
			self.r.addChild(co)

			ls = coin.SoLineSet()
			ls.numVertices.setValues(0,1,[2])
			self.r.addChild(ls)

	def show(self):
		win = SoGui.init(sys.argv[0])
		if win == None: sys.exit(1)
		viewer = SoGuiExaminerViewer(win)
		from PyQt4 import QtGui
		bgcol = QtGui.QColor(0,255,255,0)
		viewer.setBackgroundColor(bgcol)
		viewer.setSceneGraph(self.r)
		viewer.setTitle("Examiner Viewer")
		viewer.show()
		SoGui.show(win)
		SoGui.mainLoop()

	def geom(self, resolution=None):
		"""
		Method to draw the geometry of the scene to a Coin3D scenegraph.
		"""
		nod = coin.SoSeparator()
		mat = coin.SoMaterial()
		mat.diffuseColor=(1,.5,.5)
		nod.addChild(mat)
		self.r.addChild(nod)
		self.r.addChild(self.sim._asm.get_scene_graph(resolution))

	def show_geom(self, resolution=None):
		self.geom(resolution)
		self.show()

	def rays(self, escaping_len=.2, max_rays=None, resolution=None):
		"""
		Method to draw the rays to a Coin3D scenegraph. Needs to be called after a raytrace has been peroformed.
		"""

		tree = self.sim.tree
		no = coin.SoSeparator()
		
		# loop through the reflection sequences?
		co = [] # regular lines
		pos = [] # 2D level text position
		text = [] # 2D level text
		hist = {} # ray histories, for highlighted rays

		lentree = tree.num_bunds()

		for level in xrange(lentree):

			start_rays = tree[level]
			if max_rays ==  None:
				selector = None
			elif level==0:
				ordered_parents = tree.ordered_parents()
				selector = N.arange(max_rays)
			else:
				selector = N.nonzero(N.in1d(start_rays.get_parents(), selector))[0]

			sv = start_rays.get_vertices(selector)
			sd = start_rays.get_directions(selector)
			se = start_rays.get_energy(selector)
			rays = len(se)

			if level == tree.num_bunds() - 1:
				parents = []
			else:
				end_rays = tree[level + 1]
				ev = end_rays.get_vertices()
				parents = end_rays.get_parents()

			# loop through individual rays in this bundle
			for ray in xrange(rays):
				if se[ray] <= self.sim.minener:
					# ignore rays with starting energy smaller than energy cutoff
					continue
		
				if ray in parents:
					# Has a hit on another surface
					first_childs = N.nonzero(ray == parents)[0]
					c1 = sv[:,ray]
					for cs in first_childs:
						c2 = ev[:,cs]
						co += [(c1[0],c1[1],c1[2]), (c2[0],c2[1],c2[2])]

				else:
					l = escaping_len
					#if level == 0:
					#	l = 0.1
					# Escaping ray.
					c1 = sv[:,ray]
					c2 = sv[:,ray] + sd[:,ray]*l
					co += [(c1[0],c1[1],c1[2]), (c2[0],c2[1],c2[2])]

			color=(1,1-float(level)/lentree,0.5)

			no1 = coin.SoSeparator()

			ma1 = coin.SoMaterial()
			ma1.diffuseColor = color
			no1.addChild(ma1)

			ds = coin.SoDrawStyle()
			ds.style = ds.LINES
			ds.lineWidth = 2
			no1.addChild(ds)

			coor = coin.SoCoordinate3()
			coor.point.setValues(0, len(co), co)
			no1.addChild(coor)

			ls = coin.SoLineSet()
			ind = [2] * (len(co)/2)
			ls.numVertices.setValues(0, len(ind), ind)
			no1.addChild(ls)

			no.addChild(no1)

		self.r.addChild(no)

	def show_rays(self, escaping_len=.2, max_rays=None, resolution=None):
		self.rays(escaping_len, max_rays, resolution)
		self.geom(resolution)
		self.show()
