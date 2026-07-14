* GAMS-model avgasb.dag.gms written by dag2gams Converter at 29/03/2004 17:01:1
* University of Vienna
$offdigit;
 Set i/1*10/;
 Set j/1*8/;
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
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= (-2) * x('2') - 
x('3') - 
3 * x('4') - 
2 * x('5') - 
4 * x('6') - 
3 * x('7') - 
5 * x('8') + 
2 * power(x('1'), 2) + 
2 * power(x('2'), 2) + 
2 * power(x('3'), 2) + 
2 * power(x('4'), 2) + 
2 * power(x('5'), 2) + 
2 * power(x('6'), 2) + 
2 * power(x('7'), 2) + 
2 * power(x('8'), 2) - 
x('1') * x('2') - 
x('2') * x('3') - 
x('3') * x('4') - 
x('4') * x('5') - 
x('5') * x('6') - 
x('6') * x('7') - 
x('7') * x('8');


con1..-x('2') + 
3 * x('6') + 
2 * x('8') =l= 0;
con2..-x('2') + 
x('4') + 
3 * x('6') + 
5 * x('8') =l= 0;
con3..(-5) * x('1') - 
3 * x('3') + 
3 * x('5') + 
x('7') =l= 0;
con4..(-2) * x('1') - 
x('3') + 
x('7') =l= 0;
con5..x('1') + 
x('3') + 
x('5') + 
x('7') =l= 2;
con6..x('2') + 
x('4') + 
x('6') + 
x('8') =l= 2;
con7..x('7') + 
x('8') =l= 1;
con8..x('5') + 
x('6') =l= 1;
con9..x('3') + 
x('4') =l= 1;
con10..x('1') + 
x('2') =l= 1;
x.lo('1')=0;
x.up('1')=1;
x.lo('2')=0;
x.up('2')=1;
x.lo('3')=0;
x.up('3')=1;
x.lo('4')=0;
x.up('4')=1;
x.lo('5')=0;
x.up('5')=1;
x.lo('6')=0;
x.up('6')=1;
x.lo('7')=0;
x.up('7')=1;
x.lo('8')=0;
x.up('8')=1;
Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


