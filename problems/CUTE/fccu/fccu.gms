* GAMS-model fccu.dag.gms written by dag2gams Converter at 29/03/2004 16:59:07
* University of Vienna
$offdigit;
 Set i/1*8/;
 Set j/1*19/;
 Equations objcon
con1
con2
con3
con4
con5
con6
con7
con8
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= power((x('2')) - 36, 2) + 
power((x('3')) - 20, 2) + 
power((x('7')) - 4.2000000000000002, 2) + 
power((x('8')) - 0.90000000000000002, 2) + 
power((x('9')) - 3.8999999999999999, 2) + 
power((x('10')) - 2.2000000000000002, 2) + 
power((x('11')) - 22.800000000000001, 2) + 
power((x('12')) - 6.7999999999999998, 2) + 
power((x('13')) - 19, 2) + 
power((x('14')) - 8.5, 2) + 
power((x('17')) - 10.800000000000001, 2) + 
5 * power((x('1')) - 31, 2) + 
3.0000000300000003 * power((x('4')) - 3, 2) + 
3.0000000300000003 * power((x('5')) - 5, 2) + 
3.0000000300000003 * power((x('6')) - 3.5, 2) + 
3.0000000300000003 * power((x('15')) - 2.2000000000000002, 2) + 
3.0000000300000003 * power((x('16')) - 2.5, 2) + 
3.0000000300000003 * power((x('18')) - 6.5, 2) + 
3.0000000300000003 * power((x('19')) - 6.5, 2);


con1.. x('17') - 
x('18') - 
x('19') =e= 0;
con2.. x('12') - 
x('15') - 
x('16') =e= 0;
con3.. x('13') - 
x('14') - 
x('17') =e= 0;
con4.. x('11') - 
x('12') - 
x('13') =e= 0;
con5.. x('3') - 
x('10') - 
x('11') + 
x('14') =e= 0;
con6.. x('7') - 
x('8') - 
x('9') =e= 0;
con7.. x('2') - 
x('3') - 
x('4') - 
x('5') - 
x('6') - 
x('7') =e= 0;
con8.. x('1') - 
x('2') + 
x('9') =e= 0;
Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


