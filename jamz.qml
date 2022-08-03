import QtQuick 2.0
import MuseScore 3.0

MuseScore {
      menuPath: "Tools.JAMZ Export"
      description: "Export a series of images for a JAMZ session"
      version: "1.0"
      
      function removeText(){
            
      }
      
      function doRehearsalMarks(){           
            var cursor = curScore.newCursor();
            cursor.rewind(0);
            var prevTick = -1;
            
            
            var measureNo = 0
            while(cursor.nextMeasure()){
                  measureNo++;
                  //console.log("Cursor next");
                  var found = false;
                  var measure = cursor.measure;
                  
                  if(measure.nextMeasure == null){
                        addPageBreak(cursor);
                  } else if(measureNo % 2 == 0){
                        addLineBreak(cursor);
                  }
                  
                  var seg = measure.firstSegment;
                  while(seg && !found){
                        if(seg.annotations.length > 0){
                              if(seg.annotations[0].type == Element.REHEARSAL_MARK){
                                    console.log("Found rehearsal mark at tick " + seg.tick + " - adding spacer");
                                    console.log(seg.annotations[0].text);
                                    seg.annotations[0].visible = false;
                                    addPageBreak(cursor);
                                    break;
                              }
                        }
                              
                        prevTick = seg.tick;
                        
                        seg = seg.next;
                        if(seg == null || seg.tick >= measure.lastSegment.tick){
                              break;
                        }
                  }
            }
      }
      
      function addPageBreak(cursor){
            cursor.prev();
            var spacer = newElement(Element.LAYOUT_BREAK);
            spacer.layoutBreakType = LayoutBreak.PAGE;
            cursor.add(spacer);                             
            cursor.next();
     }
     
     function addLineBreak(cursor){
            cursor.prev();
            var spacer = newElement(Element.LAYOUT_BREAK);
            spacer.layoutBreakType = LayoutBreak.LINE;
            cursor.add(spacer);                             
            cursor.next();
     }
      
      function doStartSpacing(){
            console.log("Checking spacing at start...");
            var cursor = curScore.newCursor();
            cursor.rewind(0);
            
            if(cursor.element && cursor.element.type === Element.CHORD){
                  console.log("Has notes in first bar - adding spacers");
                  cmd("select-all");
                  cmd("select-begin-score");
                  cmd("insert-measure");
                  cmd("insert-measure");
            }
      }
      
      function doEndSpacing(){
            cmd("append-measure");
      }
      
      function var_dump(el){
            console.log(Object.keys(el));
      }
      
      onRun: {     
            console.log("Starting JAMZ Export for " + curScore.title);
            
            curScore.startCmd();
            
            doStartSpacing();
            doEndSpacing();
            
            doRehearsalMarks();
            
            curScore.endCmd();
            
            Qt.quit();
            }
      }
