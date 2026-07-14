* GAMS-model hs108.dag.gms written by dag2gams Converter at 29/03/2004 17:01:1
* University of Vienna
$offdigit;
 Set i/1*13/;
 Set j/1*9/;
 Equations objcon
con1
con2
con3
con4
con5
con6
con7
con8
con9
con10
con11
con12
con13
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= (-0.5) * x('1') * x('4') + 
0.5 * x('2') * x('3') - 
0.5 * x('3') * x('9') - 
0.5 * x('5') * x('8') + 
0.5 * x('5') * x('9') + 
0.5 * x('6') * x('7');


con1..x('5') * x('8') - 
x('6') * x('7') =g= 0;
con2..x('1') * x('4') - 
x('2') * x('3') =g= 0;
con3..x('3') * x('9') =g= 0;
con4..x('5') * x('9') =l= 0;
con5..-power(x('7'), 2) - 
power(x('8') - 
x('9'), 2) =g= -1;
con6..-power(x('3'), 2) - 
power(x('4'), 2) =g= -1;
con7..-power(x('3') - 
x('5'), 2) - 
power(x('4') - 
x('6'), 2) =g= -1;
con8..-power(x('5'), 2) - 
power(x('6'), 2) =g= -1;
con9..power(x('9'), 2) =l= 1;
con10..-power(x('1'), 2) - 
power(x('2') - 
x('9'), 2) =g= -1;
con11..-power(x('3') - 
x('7'), 2) - 
power(x('4') - 
x('8'), 2) =g= -1;
con12..-power(x('1') - 
x('5'), 2) - 
power(x('2') - 
x('6'), 2) =g= -1;
con13..-power(x('1') - 
x('7'), 2) - 
power(x('2') - 
x('8'), 2) =g= -1;
x.lo('9')=-0;
Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


