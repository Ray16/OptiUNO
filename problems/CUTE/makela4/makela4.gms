* GAMS-model makela4.dag.gms written by dag2gams Converter at 29/03/2004 16:59:59
* University of Vienna
$offdigit;
 Set i/1*40/;
 Set j/1*21/;
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
con14
con15
con16
con17
con18
con19
con20
con21
con22
con23
con24
con25
con26
con27
con28
con29
con30
con31
con32
con33
con34
con35
con36
con37
con38
con39
con40
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= x('21');


con1..-x('20') - 
x('21') =l= 0;
con2..x('1') - 
x('21') =l= 0;
con3..-x('19') - 
x('21') =l= 0;
con4..x('2') - 
x('21') =l= 0;
con5..-x('18') - 
x('21') =l= 0;
con6..x('3') - 
x('21') =l= 0;
con7..-x('17') - 
x('21') =l= 0;
con8..x('4') - 
x('21') =l= 0;
con9..-x('16') - 
x('21') =l= 0;
con10..x('5') - 
x('21') =l= 0;
con11..-x('15') - 
x('21') =l= 0;
con12..x('6') - 
x('21') =l= 0;
con13..-x('14') - 
x('21') =l= 0;
con14..x('7') - 
x('21') =l= 0;
con15..-x('13') - 
x('21') =l= 0;
con16..x('8') - 
x('21') =l= 0;
con17..-x('12') - 
x('21') =l= 0;
con18..x('9') - 
x('21') =l= 0;
con19..-x('11') - 
x('21') =l= 0;
con20..x('10') - 
x('21') =l= 0;
con21..-x('10') - 
x('21') =l= 0;
con22..x('11') - 
x('21') =l= 0;
con23..-x('9') - 
x('21') =l= 0;
con24..x('12') - 
x('21') =l= 0;
con25..-x('8') - 
x('21') =l= 0;
con26..x('13') - 
x('21') =l= 0;
con27..-x('7') - 
x('21') =l= 0;
con28..x('14') - 
x('21') =l= 0;
con29..-x('6') - 
x('21') =l= 0;
con30..x('15') - 
x('21') =l= 0;
con31..-x('5') - 
x('21') =l= 0;
con32..x('16') - 
x('21') =l= 0;
con33..-x('4') - 
x('21') =l= 0;
con34..x('17') - 
x('21') =l= 0;
con35..-x('3') - 
x('21') =l= 0;
con36..x('18') - 
x('21') =l= 0;
con37..-x('2') - 
x('21') =l= 0;
con38..x('19') - 
x('21') =l= 0;
con39..-x('1') - 
x('21') =l= 0;
con40..x('20') - 
x('21') =l= 0;
Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


