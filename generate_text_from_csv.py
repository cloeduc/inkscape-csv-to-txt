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

import sys,inkex,copy,simpletransform,re

class CSVGenerator(inkex.Effect):
  def __init__(self):
      # Call the base class constructor.
      inkex.Effect.__init__(self)
      self.OptionParser.add_option('--csv_file',action='store',type='string', dest='csv_file',default="PathFile")
      self.OptionParser.add_option('--elements_in_raw',action='store',type='int', dest='elements_in_raw',default=6)
      self.OptionParser.add_option('--delimiter_color',action='store',type='string', dest='delimiter_color',default='#ff00ff')
      self.OptionParser.add_option('--text_to_replace',action='store',type='string', dest='text_to_replace',default='TEXT_TO_REPLACE')
      self.OptionParser.add_option('--csv_delimiter',action='store',type='string', dest='csv_delimiter',default=',')

  def effect(self):
    if self.selected:
      delimiter_color = self.options.delimiter_color
      hex = re.search('#((?:[A-f0-9]{3}){1,2})', delimiter_color)
      if(hex is None):
        inkex.debug("Please enter a hexadecimal color for the delimiter_color option")
        return
      parent = self.current_layer
      pinkRect = self.getLineOutRect()
      textNodes = self.getTextNodes()
      csv_delimiter = self.options.csv_delimiter
      if(pinkRect is False):
        inkex.debug("Items Must be surrounded with a "+delimiter_color+" rectangle")
        return
      file_object  = open(self.options.csv_file, 'r');
      lineOutWidth = float(pinkRect.attrib.get('width'))
      lineOutHeight = float(pinkRect.attrib.get('height'))
      xtranslate=0
      ytranslate=0
      for line in file_object:
        txt_to_replace = line.decode('utf-8')
        txt_to_replace_list = txt_to_replace.split(csv_delimiter)
        txt_to_search_list = self.options.text_to_replace.split(csv_delimiter)
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
          if (node != pinkRect and node not in textNodes):
            self.moveNode(xtranslate, ytranslate, newNode, parent)
        #After all, move text node
        for textNode in textNodes:
          newTextNode = copy.deepcopy(textNode);
          if newTextNode.tag == '{http://www.w3.org/2000/svg}text':
            for children in newTextNode.getchildren():
              if children.text in txt_to_search_list:
                children.text = txt_to_replace_list[txt_to_search_list.index(children.text)]
          if newTextNode.tag == '{http://www.w3.org/2000/svg}flowRoot':
            for children in newTextNode.getchildren():
              if children.tag == '{http://www.w3.org/2000/svg}flowPara':
                if children.text in txt_to_search_list:
                  children.text = txt_to_replace_list[txt_to_search_list.index(children.text)]
          self.moveNode(xtranslate, ytranslate, newTextNode, parent)
    else:
      inkex.debug("Please select a element with "+delimiter_color+" rectangle  (for delimiter)")
  def getLineOutRect(self):
    for id, node in self.selected.iteritems():
      if node.tag == '{http://www.w3.org/2000/svg}rect' and node.attrib.get('style').find('stroke:'+self.options.delimiter_color) > -1 :
        return node
    return False
  def getTextNodes(self):
    txt_to_replace_list = self.options.text_to_replace.split(self.options.csv_delimiter)
    nodes = []
    for id, node in self.selected.iteritems():
      if node.tag == '{http://www.w3.org/2000/svg}text':
        for children in node.getchildren():
          if children.text in txt_to_replace_list:
            nodes.append(children)
      if node.tag == '{http://www.w3.org/2000/svg}flowRoot':
        for children in node.getchildren():
          if children.tag == '{http://www.w3.org/2000/svg}flowPara':
            if children.text in txt_to_replace_list:
              nodes.append(node)
    if(len(nodes)>0):
      return nodes
    return False
  def moveNode(self, x, y, node, layer):
    transformation = 'translate(' + str(x) + ', ' + str(y) + ')'
    transform = simpletransform.parseTransform(transformation)
    simpletransform.applyTransformToNode(transform, node)
    layer.append(node)

effect = CSVGenerator()
effect.affect()
