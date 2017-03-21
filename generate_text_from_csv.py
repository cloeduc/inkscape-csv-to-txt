#! /usr/bin/env python
# coding: utf8
"""
csvfile-generator.py
A module to generate nodes with texts from a csv file
Cloe Duc; mail@cloeduc.com

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

For a copy of the GNU General Public License
write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
"""

"""
Change in version 0.1.
"""
__version__ = "0.1"

import sys,inkex,simplestyle,gettext,copy,simpletransform
_ = gettext.gettext

class CSVGenerator(inkex.Effect):
  def __init__(self):
      # Call the base class constructor.
      inkex.Effect.__init__(self)
      self.OptionParser.add_option('--csv_file',action='store',type='string', dest='csv_file')
      self.OptionParser.add_option('--elements_in_raw',action='store',type='int', dest='elements_in_raw',default=6)
      self.OptionParser.add_option('--text_to_replace',action='store',type='string', dest='text_to_replace',default='PLOP')

  def effect(self):
    if self.selected:
      parent = self.current_layer
      pinkRect = self.getLineOutRect();
      textNode = self.getTextNode();
      if(pinkRect is not False and textNode is not False):
        file_object  = open(self.options.csv_file, 'r');
        lineOutWidth = float(pinkRect.attrib.get('width'))
        lineOutHeight = float(pinkRect.attrib.get('height'))
        xtranslate=0
        ytranslate=0
        for line in file_object:
          txt_to_replace = line.decode('utf-8')
          #first move pink rectangle
          xtranslate = xtranslate+lineOutWidth
          #New raw
          if(xtranslate >= lineOutWidth*self.options.elements_in_raw):
            xtranslate = 0
            ytranslate = ytranslate+lineOutHeight
          self.moveNode(xtranslate, ytranslate, copy.deepcopy(pinkRect), parent)
          #copy and move all other nodes
          for id, node in self.selected.iteritems():
            newNode = copy.deepcopy(node)
            #Replace node text
            if (node != pinkRect and node != textNode):
              self.moveNode(xtranslate, ytranslate, newNode, parent)
          #After all, move text node
          newTextNode = copy.deepcopy(textNode);
          for children in newTextNode.getchildren():
            if children.text == self.options.text_to_replace:
              children.text = txt_to_replace
          self.moveNode(xtranslate, ytranslate, newTextNode, parent)
      else:
        inkex.debug("Items Must be surrounded with au pink rectangle and have a text node with '"+self.options.text_to_replace+"'")
    else:
      inkex.debug("Please select a element with a pink rectangle (for delimiter) and, at least a text object with the text :"+self.options.text_to_replace)
  def getLineOutRect(self):
    for id, node in self.selected.iteritems():
      if node.tag == '{http://www.w3.org/2000/svg}rect' and node.attrib.get('style') == 'fill:none;fill-opacity:1;stroke:#ff00ff;stroke-width:0.99921262;stroke-miterlimit:4;stroke-dasharray:none':
        return node
    return False
  def getTextNode(self):
    for id, node in self.selected.iteritems():
      if node.tag == '{http://www.w3.org/2000/svg}text':
        for children in node.getchildren():
          if children.text == self.options.text_to_replace:
            return node
    return False
  def moveNode(self, x, y, node, layer):
    transformation = 'translate(' + str(x) + ', ' + str(y) + ')'
    transform = simpletransform.parseTransform(transformation)
    simpletransform.applyTransformToNode(transform, node)
    layer.append(node)

effect = CSVGenerator()
effect.affect()
