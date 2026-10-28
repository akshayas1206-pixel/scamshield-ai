const $=id=>document.getElementById(id);
let checks=0, flags=0, history=[];
function renderResult(target,data,type="message"){
 const box=$(target); box.classList.remove("hidden","risk-high","risk-caution","risk-low");
 const level=(data.level||"").toLowerCase();
 box.classList.add(level.includes("high")?"risk-high":(level.includes("caution")||level.includes("needs")?"risk-caution":"risk-low"));
 box.innerHTML=`<h3>${escapeHtml(data.level||"Result")}${type==="message"&&Number.isFinite(data.score)?` · ${data.score}/100`:""}</h3><ul>${(data.reasons||[]).map(x=>`<li>${escapeHtml(x)}</li>`).join("")}</ul>${data.advice?`<p>${escapeHtml(data.advice)}</p>`:""}`;
}
function escapeHtml(s){return String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
function addHistory(label,level){history.unshift({label:label.slice(0,70),level});history=history.slice(0,8);$("historyList").innerHTML=history.map(x=>`<div class="history-item"><span>${escapeHtml(x.label)}</span><strong>${escapeHtml(x.level)}</strong></div>`).join("")||"Your recent checks will appear here during this session.";}
$("analyzeBtn").addEventListener("click",async()=>{
 const message=$("message").value.trim();if(!message){$("message").focus();return;}
 const r=await fetch("/api/analyze",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({message})});const data=await r.json();
 renderResult("messageResult",data);checks++;if(data.score>=60)flags++;$("checks").textContent=checks;$("flags").textContent=flags;addHistory(message,data.level);
});
$("exampleBtn").addEventListener("click",()=>{$("message").value="URGENT! Your bank account will be suspended today. Click here to verify your account and share your OTP to claim your reward.";});
$("clearBtn").addEventListener("click",()=>{$("message").value="";$("messageResult").classList.add("hidden");});
$("urlBtn").addEventListener("click",async()=>{
 const url=$("urlInput").value.trim();if(!url){$("urlInput").focus();return;}
 const r=await fetch("/api/check-url",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({url})});const data=await r.json();renderResult("urlResult",data,"url");addHistory(url,data.level);
});
$("clearHistory").addEventListener("click",()=>{history=[];$("historyList").textContent="Your recent checks will appear here during this session.";});
