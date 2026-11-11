const pptxgen = require('pptxgenjs');
const fs = require('fs');
const path = require('path');
const pptx = new pptxgen();
pptx.layout='LAYOUT_WIDE';
pptx.author='Student group — academic draft';
pptx.subject='Problem 8, Lossless Data Compression — V4 reproducibility and header audit';
pptx.title='Problem 8 — Lossless Data Compression';
pptx.lang='en-US';
const W=13.333, H=7.5;
const C={bg:'0C1527',bg2:'14213A',card:'1D2B45',card2:'22334F',muted:'A8B7CA',white:'F7FAFF',purple:'AB91FF',cyan:'5CD1DA',green:'80D6AE',amber:'F3C477',red:'F28F99',line:'344660'};
const SH=pptx.ShapeType;
const p=(v)=>v;
function addBG(s){s.background={color:C.bg};s.addShape(SH.rect,{x:0,y:0,w:W,h:.12,line:{color:C.purple,transparency:100},fill:{color:C.purple}});s.addShape(SH.ellipse,{x:11.68,y:-1.2,w:3,h:3,line:{color:C.purple,transparency:100},fill:{color:C.purple,transparency:93}});}
function txt(s,text,x,y,w,h,size=16,color=C.white,extra={}){s.addText(text,{x,y,w,h,fontFace:'Aptos',fontSize:size,color,margin:0,breakLine:false,fit:'shrink',...extra});}
function title(s,num,heading,desc=''){addBG(s);txt(s,String(num).padStart(2,'0')+'  /  PROBLEM 8',.65,.35,7,.21,9,C.cyan,{bold:true,charSpacing:1.5});txt(s,heading,.65,.74,12.02,.52,28,C.white,{bold:true});if(desc)txt(s,desc,.68,1.34,12,.42,14,C.muted);s.addShape(SH.line,{x:.65,y:6.99,w:12.03,h:0,line:{color:C.line,width:1}});txt(s,'Lossless Data Compression  •  Assignment pages 31–34',.67,7.1,10,.18,8,C.muted);txt(s,String(num)+' / 13',11.77,7.1,.89,.18,8,C.muted,{align:'right'});}
function round(s,x,y,w,h,fill=C.card,rad=.18,stroke=C.line){s.addShape(SH.roundRect,{x,y,w,h,rectRadius:rad,fill:{color:fill},line:{color:stroke,width:.7},radius:rad});}
function pill(s,text,x,y,w,fill=C.card2,col=C.white){round(s,x,y,w,.37,fill,.14,fill);txt(s,text,x+.07,y+.085,w-.14,.19,10,col,{bold:true,align:'center'});}
function bullet(s,text,x,y,w,size=16,color=C.white){txt(s,'•',x,y,.18,.27,size,C.cyan,{bold:true});txt(s,text,x+.24,y,w-.24,.39,size,color);}
function line(s,x1,y1,x2,y2,color=C.line,width=2){s.addShape(SH.line,{x:x1,y:y1,w:x2-x1,h:y2-y1,line:{color,width}});}
function chip(s,label,value,x,y,w,col=C.purple){round(s,x,y,w,1.15,C.card);txt(s,label,x+.15,y+.12,w-.3,.22,11,C.muted);txt(s,value,x+.15,y+.44,w-.3,.48,26,col,{bold:true});}
function cardTitle(s,heading,text,x,y,w,h,color=C.cyan){round(s,x,y,w,h);s.addShape(SH.rect,{x:x+.19,y:y+.21,w:.055,h:.40,fill:{color},line:{color,transparency:100}});txt(s,heading,x+.4,y+.19,w-.55,.35,17,C.white,{bold:true});txt(s,text,x+.4,y+.69,w-.58,h-.78,13,C.muted);}

// 1 cover
{
let s=pptx.addSlide();addBG(s);
round(s,.8,.85,2.0,.4,C.card2);txt(s,'DATA STRUCTURES & ALGORITHMS',.9,.97,1.8,.15,9,C.cyan,{bold:true});
txt(s,'LOSSLESS\nDATA COMPRESSION',.8,1.73,8.7,1.67,38,C.white,{bold:true,breakLine:false});
txt(s,'Fixed-length  →  RLE  →  Huffman  →  Canonical Huffman  →  LZ77',.82,3.76,9.9,.55,18,C.muted);
s.addShape(SH.ellipse,{x:9.58,y:1.65,w:2.37,h:2.37,line:{color:C.purple,width:3},fill:{color:C.card}});
txt(s,'0 1\n1 0\n0 1',10.13,2.08,1.26,1.46,24,C.cyan,{bold:true,align:'center',fontFace:'Aptos Mono'});
line(s,9.65,5.2,12.35,5.2,C.purple,4);
txt(s,'THEORY  +  NOTEBOOK  +  EMPIRICAL EVIDENCE',.82,5.48,9,.28,12,C.green,{bold:true,charSpacing:.6});
txt(s,'Group: [names to add]    |    Submission deadline: [verify]',.82,6.62,10.7,.25,12,C.muted);
}
//2
{
let s=pptx.addSlide();title(s,2,'What must be submitted','The handwritten component is indispensable; code and slides must agree with it.');
cardTitle(s,'HANDWRITTEN SOLUTIONS','Q1–Q5: every calculation, heap merge, bitstream trace, canonical assignment, sliding-window trace, and complexity analysis.',.68,2.04,3.93,3.33,C.red);
cardTitle(s,'WORKING CODE','All five compression/decompression pairs in Python, 20 required dataset round trips, plots and reproducible notebook.',4.72,2.04,3.93,3.33,C.cyan);
cardTitle(s,'SLIDE PRESENTATION','Readable academic explanation of methods and results, plus an actual link to the team GitHub repository.',8.77,2.04,3.88,3.33,C.purple);
round(s,.68,5.69,11.95,.64,'382736',.12,'734455');txt(s,'CRITICAL: Without handwritten work, the professor will not consider the submission.',.96,5.90,11.4,.22,14,C.red,{bold:true});
}
//3
{
let s=pptx.addSlide();title(s,3,'Five stages of increasing sophistication','Each version targets a limitation left by its predecessor.');
const stages=[['V1','FIXED','Same bits\nfor all symbols'],['V2','RLE','Consecutive\nidentical runs'],['V3','HUFFMAN','Statistical\nfrequency skew'],['V4','CANONICAL','Codes reconstructed\nfrom lengths'],['V5','LZ77 + HUFF','Repeated phrases\nwithin a window']];
for(let i=0;i<5;i++){let x=.6+i*2.55;round(s,x,2.11,2.33,3.08,i%2?C.card:C.card2);pill(s,stages[i][0],x+.17,2.34,.59,C.purple,C.bg);txt(s,stages[i][1],x+.18,3.03,2.05,.33,18,C.white,{bold:true});txt(s,stages[i][2],x+.18,3.66,2.0,.85,15,C.muted);if(i<4)txt(s,'›',x+2.33,3.19,.23,.47,25,C.cyan,{bold:true,align:'center'});}
txt(s,'Lossless means: decompress(compress(data)) == data — for every valid input.',.83,5.81,11.8,.5,18,C.green,{bold:true});
}
//4
{
let s=pptx.addSlide();title(s,4,'Theoretical comparison: 100 symbols','Alphabet: A45, B13, C12, D16, E9, F5 — six distinct symbols.');
chip(s,'V1 • fixed-length','300 bits',.72,2.04,2.77,C.white);chip(s,'V2 • 6 contiguous runs','60 bits',3.66,2.04,2.76,C.cyan);chip(s,'V2 • 100 separate runs','1,000 bits',6.59,2.04,2.78,C.red);chip(s,'V3 / V4 • Huffman','224 bits',9.53,2.04,2.85,C.green);
round(s,.78,3.68,11.78,1.61,C.card2);txt(s,'Shannon entropy',1.04,3.91,2.85,.32,18,C.white,{bold:true});txt(s,'H(X) = −Σ pᵢ log₂(pᵢ) = 2.219880 bits/symbol',4.2,3.98,7.5,.42,20,C.purple,{bold:true});
txt(s,'100 × H(X) = 221.988 theoretical bits',1.03,4.69,7.7,.36,20,C.white,{bold:true});
txt(s,'Huffman gap: only 2.012 bits above entropy bound.',.88,5.77,11.7,.35,17,C.muted);
}
//5
{
let s=pptx.addSlide();title(s,5,'Huffman: five min-heap merges','The two smallest subtrees are combined at each step.');
round(s,.69,1.91,4.55,4.56,C.card2);
const steps=[['01','F5 + E9','14'],['02','C12 + B13','25'],['03','14 + D16','30'],['04','25 + 30','55'],['05','A45 + 55','100']];
for(let i=0;i<steps.length;i++){let y=2.22+i*.78;pill(s,steps[i][0],.93,y,.52,C.purple,C.bg);txt(s,steps[i][1],1.63,y+.06,2.43,.31,18,C.white,{bold:i===4});txt(s,'→ '+steps[i][2],4.0,y+.07,1.01,.30,15,C.cyan,{bold:true});}
// tree nodes on right; connectors first
const nd={root:[9.6,2.12],a:[7.9,3.04],n55:[10.8,3.04],n25:[9.70,3.95],n30:[11.75,3.95],c:[8.88,4.85],b:[10.0,4.85],n14:[11.30,4.85],d:[12.23,4.85],f:[10.92,5.78],e:[11.82,5.78]};
const edges=[['root','a',0],['root','n55',1],['n55','n25',0],['n55','n30',1],['n25','c',0],['n25','b',1],['n30','n14',0],['n30','d',1],['n14','f',0],['n14','e',1]];
for(let [u,v,bit] of edges){let x1=nd[u][0]+.35,y1=nd[u][1]+.25,x2=nd[v][0]+.35,y2=nd[v][1]+.25;line(s,x1,y1,x2,y2,C.line,2);txt(s,String(bit),(x1+x2)/2-.11,(y1+y2)/2-.10,.22,.25,10,C.cyan,{bold:true});}
const names={root:'100',a:'A45',n55:'55',n25:'25',n30:'30',c:'C12',b:'B13',n14:'14',d:'D16',f:'F5',e:'E9'};
for(let key in nd){let [x,y]=nd[key];s.addShape(SH.ellipse,{x,y,w:.72,h:.52,line:{color:key.startsWith('n')||key==='root'?C.purple:C.cyan,width:1.6},fill:{color:key.startsWith('n')||key==='root'?C.card2:'173D47'}});txt(s,names[key],x+.035,y+.155,.64,.20,11,C.white,{bold:true,align:'center'});}
txt(s,'Read each path root → leaf: left=0, right=1',5.56,6.4,6.8,.27,12,C.muted);
}
//6
{
let s=pptx.addSlide();title(s,6,'Prefix-free codes make decoding unambiguous','Stage 3 codewords: A=0, B=101, C=100, D=111, E=1101, F=1100.');
round(s,.75,2.12,11.85,1.15,C.card2);txt(s,'INPUT   0 1 0 1 0 1 1 0 0 1 1 1 0',1.02,2.42,10.9,.46,25,C.white,{bold:true,fontFace:'Aptos Mono',charSpacing:1});
const blocks=[['0','A'],['101','B'],['0','A'],['1100','F'],['111','D'],['0','A']];let x=1.01;let widths=[1.35,1.92,1.35,2.27,1.93,1.35];
for(let i=0;i<6;i++){let w=widths[i];round(s,x,3.69,w,1.22,i%2?C.card2:C.card);txt(s,blocks[i][0],x,3.89,w,.36,21,C.cyan,{bold:true,align:'center',fontFace:'Aptos Mono'});txt(s,blocks[i][1],x,4.39,w,.32,19,C.white,{bold:true,align:'center'});x+=w+.16;}
txt(s,'Decoded message:  A B A F D A',1.03,5.51,10.4,.48,25,C.green,{bold:true});
txt(s,'No code is the prefix of another → every leaf ends exactly one symbol.',1.04,6.25,11.9,.33,16,C.muted);
}
//7
{
let s=pptx.addSlide();title(s,7,'Canonical Huffman: deterministic codebook','With a known symbol alphabet/order, lengths determine canonical codes.');
round(s,.73,1.94,11.92,.75,C.card2);txt(s,'code_next = (code_previous + 1) << (new_length − previous_length)',1.00,2.19,11.3,.31,19,C.cyan,{bold:true,fontFace:'Aptos Mono'});
const rows=[['A','1','0','0'],['B','3','(0+1) << 2 = 4','100'],['C','3','(4+1) << 0 = 5','101'],['D','3','(5+1) << 0 = 6','110'],['E','4','(6+1) << 1 = 14','1110'],['F','4','(14+1) << 0 = 15','1111']];
const hdr=['SYMBOL','LENGTH','ASSIGNMENT','CANONICAL CODE'];const cols=[1.02,2.55,4.53,9.04],colW=[1.22,1.48,4.24,3.13];
for(let i=0;i<4;i++)txt(s,hdr[i],cols[i],2.94,colW[i],.28,11,C.muted,{bold:true});
for(let r=0;r<6;r++){let y=3.33+r*.44;round(s,.84,y,11.66,.39,r%2?C.card2:C.card,.04,r%2?C.card2:C.card);for(let i=0;i<4;i++)txt(s,rows[r][i],cols[i],y+.075,colW[i],.25,14,i===3?C.green:C.white,{bold:i===3});}
round(s,.86,6.22,11.63,.5,C.card2);txt(s,'224-bit payload unchanged. Standalone V4 stores symbol + length pairs; headers may be larger.',1.11,6.38,11.13,.24,13,C.cyan,{bold:true});
}
//8
{
let s=pptx.addSlide();title(s,8,'LZ77 sliding-window: seven emitted triples','S = ABRACADABRA_ABRACADABRA  •  W = 12  •  L = 12  •  “_” represents a space.');
const colx=[.91,1.67,3.08,7.45,10.65], widths=[.6,1.18,4.08,2.85,1.05];
for(let i=0;i<5;i++)txt(s,['STEP','p','SEARCH BUFFER','TRIPLE (offset,len,next)','NEW p'][i],colx[i],1.98,widths[i],.3,12,C.muted,{bold:true});
let rws=[['1','0','—','(0,0,A)','1'],['2','1','A','(0,0,B)','2'],['3','2','AB','(0,0,R)','3'],['4','3','ABR','(3,1,C)','5'],['5','5','ABRAC','(2,1,D)','7'],['6','7','ABRACAD','(7,4,_)','12'],['7','12','ABRACADABRA_','(12,10,A)','23']];
for(let i=0;i<7;i++){let y=2.42+i*.52;round(s,.78,y,11.8,.45,i==6?'243F47':(i%2?C.card2:C.card),.035);for(let j=0;j<5;j++)txt(s,rws[i][j],colx[j],y+.095,widths[j],.29,14,j===3?C.cyan:C.white,{bold:i===6,fontFace:j===2||j===3?'Aptos Mono':'Aptos'});}
round(s,.84,6.27,11.66,.48,C.card2);txt(s,'Final step reserves one trailing “A” as next_char: 10 matched bytes + 1 literal.',1.10,6.42,11.20,.23,13,C.green,{bold:true});
}
//9
{
let s=pptx.addSlide();title(s,9,'Q5 — Time, memory, and compression capability','Encoder-focused bounds; N=input length, m=alphabet size, W=window, L=lookahead.');
const x=[.76,2.15,5.06,7.17,9.48], ww=[1.29,2.85,2.0,2.20,3.03];let head=['STAGE','ENCODE TIME','AUX SPACE','HEADER','BEST AT'];
for(let j=0;j<5;j++)txt(s,head[j],x[j],2.02,ww[j],.28,11,C.cyan,{bold:true});
let rows=[
['V1 fixed','O(N + m)','O(m)','Alphabet / width','Simple baseline'],
['V2 RLE','O(N)','O(1) streaming','Minimal','Long same-symbol runs'],
['V3 tree','O(N + m log m)','O(m)','Tree structure','Skewed byte frequencies'],
['V4 canon.','O(N + m log m)','O(m)','Symbol + length','Skewed bytes; varies'],
['V5 LZ77','O(NWL + m′ log m′)','O(N+W+m′) batch','Several codebooks','Repeated multi-byte phrases']
];
for(let i=0;i<5;i++){let y=2.52+i*.71;round(s,.65,y,12.08,.62,i%2?C.card2:C.card);for(let j=0;j<5;j++)txt(s,rows[i][j],x[j],y+.17,ww[j],.35,j===0?14:13,j===0?C.white:C.muted,{bold:j===0});}
round(s,.72,6.30,11.89,.44,C.card2);txt(s,'V5’s conservative worst-case LZ77 matching bound is O(NWL); faster indexed search in typical inputs.',.95,6.43,11.42,.20,12,C.green);
}
//10
{
let s=pptx.addSlide();title(s,10,'Implementation: 20/20 exact round trips','Five encoders × four datasets; every decompressor reproduces its input byte-for-byte.');
chip(s,'REQUIRED ROUND-TRIP TESTS','20 / 20 PASS',.72,2.03,4.04,C.green);
cardTitle(s,'LONG RUNS','A×5000 + B×5000\n10,000 bytes',5.03,1.96,3.69,1.36,C.cyan);
cardTitle(s,'SKEWED DNA','A 70%; C,G,T 10% each\n12,000 bytes',8.91,1.96,3.70,1.36,C.cyan);
cardTitle(s,'PYTHON SOURCE','Pinned .py source snapshot\n50 KiB',.72,3.52,3.93,1.39,C.purple);
cardTitle(s,'RANDOM BYTES','Pinned os.urandom sample\n10,000 bytes',4.86,3.52,3.92,1.39,C.purple);
cardTitle(s,'EXTRA TESTING','Empty input, one symbol, binary data, overlaps, 256 symbols.',8.97,3.52,3.64,1.39,C.green);
round(s,.76,5.5,11.78,.7,C.card2);txt(s,'Metrics: packet bits/original byte (header included) + encoder/decoder throughput in MiB/s.',1.05,5.73,11.16,.28,16,C.white,{bold:true});
}
//11
{
let s=pptx.addSlide();title(s,11,'Compression ratio vs. entropy','Identical SHA256-pinned inputs; complete packet sizes include headers. Dashed=8.0; dotted=H₀.');
const pos=[[.67,1.87],[6.78,1.87],[.67,4.34],[6.78,4.34]];
for(let i=1;i<=4;i++){const img=path.join(__dirname,'figures',`ratio_${i}.png`);round(s,pos[i-1][0],pos[i-1][1],5.9,2.36,'FFFFFF',.08,'FFFFFF');s.addImage({path:img,x:pos[i-1][0]+.04,y:pos[i-1][1]+.03,w:5.82,h:2.30});}
}
//12
{
let s=pptx.addSlide();title(s,12,'Encoding and decoding throughput','Median of 5 runs after 1 warm-up; input bytes pinned; rates depend on CPU and system load.');
const pos=[[.67,1.87],[6.78,1.87],[.67,4.34],[6.78,4.34]];
for(let i=1;i<=4;i++){const img=path.join(__dirname,'figures',`throughput_${i}.png`);round(s,pos[i-1][0],pos[i-1][1],5.9,2.36,'FFFFFF',.08,'FFFFFF');s.addImage({path:img,x:pos[i-1][0]+.04,y:pos[i-1][1]+.03,w:5.82,h:2.30});}
}
//13
{
let s=pptx.addSlide();title(s,13,'Conclusion & submission readiness','V4: verified corpus hashes, unified benchmarks, corrected Q4 space byte, and honest header tradeoffs.');
cardTitle(s,'EMPIRICAL RESULTS','Runs: RLE or LZ77\nSkewed DNA: Huffman\nPython source: LZ77+Huffman\nUniform random: generally expands',.77,1.96,5.76,3.43,C.green);
cardTitle(s,'TECHNICAL LIMITATIONS','V4 metadata may exceed V3 tree metadata. Pinned random-input PACKETS: V4 10,520 B vs V3 10,326 B. V5 is custom, not RFC DEFLATE.',6.74,1.96,5.77,3.43,C.amber);
round(s,.82,5.67,11.64,.64,C.card2);txt(s,'GITHUB: [REPLACE WITH YOUR VERIFIED REPOSITORY URL]',1.09,5.85,11.11,.29,17,C.cyan,{bold:true});
txt(s,'Still required: physically handwritten pages + group details + confirmed deadline + GitHub upload.',.83,6.51,11.63,.29,14,C.red,{bold:true});
}

pptx.writeFile({fileName:path.join(__dirname,'Problem8_Compression_Presentation.pptx')}).then(()=>console.log('Wrote 13-slide PowerPoint')).catch(err=>{console.error(err);process.exit(1)});
