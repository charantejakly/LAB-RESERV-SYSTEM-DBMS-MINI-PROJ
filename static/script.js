let inventory=[];
let currentReservationId = null;

loadDashboard();
loadInventory();
loadHistory();

function loadDashboard(){
    fetch("/api/dashboard")
    .then(r=>r.json())
    .then(data=>{
        document.getElementById("totalItems").innerHTML=data.total_items;
        document.getElementById("availableItems").innerHTML=data.available;
        document.getElementById("reservedItems").innerHTML=data.reserved;
        document.getElementById("users").innerHTML=data.users;
    });
}

function loadInventory(){
    fetch("/api/inventory")
    .then(r=>r.json())
    .then(data=>{
        inventory=data;
        displayInventory(data);
    });
}

function displayInventory(data){
    let grid=document.getElementById("inventory-grid");
    if (!grid) return;
    grid.innerHTML="";
    data.forEach(item=>{
        let percentage = item.total_qty > 0 ? (item.available_qty / item.total_qty) * 100 : 0;
        let isAvailable = item.available_qty > 0;
        
        let statusBadge = isAvailable ? 
            `<span class="w-2 h-2 rounded-full bg-secondary-container"></span><span class="text-xs text-on-surface-variant font-medium">Available</span>` :
            `<span class="w-2 h-2 rounded-full bg-error"></span><span class="text-xs text-error font-medium">Out of Stock</span>`;
            
        let reserveBtnClass = isAvailable ? 
            `bg-primary text-on-primary hover:bg-[#005a6a]` : 
            `bg-surface-variant text-on-surface-variant cursor-not-allowed opacity-50`;
            
        grid.innerHTML+=`
        <div class="bento-card flex flex-col overflow-hidden group">
            <div class="h-40 bg-surface-container-low relative border-b border-outline-variant overflow-hidden">
                <div class="absolute inset-0 bg-gradient-to-br from-surface-container to-surface-container-highest flex items-center justify-center text-outline">
                    <span class="material-symbols-outlined text-4xl" data-icon="memory">memory</span>
                </div>
                <div class="absolute top-3 right-3 px-2 py-1 bg-surface-bright/90 backdrop-blur rounded text-xs font-mono font-bold text-on-surface shadow-sm">
                    LAB-${String(item.id).padStart(3, '0')}
                </div>
            </div>
            <div class="p-5 flex flex-col flex-1">
                <h4 class="font-bold text-on-surface text-lg mb-1">${item.component_name}</h4>
                <div class="flex items-center gap-2 mb-4">
                    ${statusBadge}
                </div>
                <div class="mt-auto">
                    <div class="flex justify-between text-xs mb-1.5">
                        <span class="text-on-surface-variant">Availability</span>
                        <span class="font-mono text-on-surface font-medium">${item.available_qty}/${item.total_qty}</span>
                    </div>
                    <div class="w-full bg-surface-container-high rounded-full h-1.5 mb-4 overflow-hidden">
                        <div class="${isAvailable ? 'bg-secondary-container' : 'bg-error'} h-1.5 rounded-full" style="width: ${percentage}%"></div>
                    </div>
                    <div class="grid grid-cols-2 gap-2">
                        <button class="py-2 px-3 border border-outline-variant text-on-surface-variant rounded-lg text-xs font-medium hover:bg-surface-container transition-colors">Details</button>
                        <button ${isAvailable ? `onclick="openReserveModal(${item.id}, '${item.component_name}', ${item.available_qty}, ${item.total_qty})"` : "disabled"} 
                            class="py-2 px-3 rounded-lg text-xs font-semibold transition-colors shadow-sm ${reserveBtnClass}">Reserve</button>
                    </div>
                </div>
            </div>
        </div>
        `;
    });
}

function searchInventory(){
    let searchBox = document.getElementById("searchBox");
    if(!searchBox) return;
    let text=searchBox.value.toLowerCase();
    let filtered=inventory.filter(item=>
        item.component_name.toLowerCase().includes(text)
    );
    displayInventory(filtered);
}

function openReserveModal(id, name, available, total) {
    let student=document.getElementById("studentName")?.value;
    if(!student){
        showToast("Enter Student Name in toolbar first", "error");
        return;
    }
    
    currentReservationId = id;
    document.getElementById('modalEquipmentName').innerText = name;
    document.getElementById('modalEquipmentId').innerText = "LAB-" + String(id).padStart(3, '0');
    document.getElementById('modalAvailability').innerText = `${available}/${total} Available`;
    
    document.getElementById('reserveModal').classList.remove('hidden');
}

function closeModal() {
    currentReservationId = null;
    document.getElementById('reserveModal').classList.add('hidden');
}

function confirmReservation(){
    if(!currentReservationId) return;
    let student=document.getElementById("studentName").value;
    let role=document.getElementById("role").value;
    
    let id = currentReservationId;
    closeModal();

    fetch("/api/reserve",{
        method:"POST",
        headers:{
            "Content-Type":"application/json"
        },
        body:JSON.stringify({
            student_name:student,
            role:role,
            inventory_id:id
        })
    })
    .then(r=>r.json())
    .then(data=>{
        showToast(data.message, data.message.includes("success") ? "success" : "error");
        loadDashboard();
        loadInventory();
        loadHistory();
    });
}

function loadHistory(){
    fetch("/api/reservations")
    .then(r=>r.json())
    .then(data=>{
        let tbody=document.getElementById("history-tbody");
        if (!tbody) return;
        tbody.innerHTML="";
        data.forEach(item=>{
            let isActive = item.status === "Active";
            let statusBadge = isActive ? 
                `<span class="inline-flex items-center gap-1.5 py-1 px-2.5 rounded-full text-xs font-medium bg-tertiary-container/10 text-tertiary-container border border-tertiary-container/20">
                    <span class="w-1.5 h-1.5 rounded-full bg-tertiary-container"></span>
                    Active
                </span>` : 
                `<span class="inline-flex items-center gap-1.5 py-1 px-2.5 rounded-full text-xs font-medium bg-surface-container text-on-surface-variant border border-outline-variant">
                    <span class="w-1.5 h-1.5 rounded-full bg-outline"></span>
                    Returned
                </span>`;
                
            let actionBtn = isActive ? 
                `<button onclick="returnItem(${item.id})" class="text-secondary font-medium hover:text-[#005236] transition-colors text-sm">Return Equipment</button>` :
                `<span class="text-outline-variant text-sm">-</span>`;
                
            tbody.innerHTML+=`
            <tr class="hover:bg-surface-container-lowest transition-colors">
                <td class="px-6 py-4 font-mono font-medium text-on-surface">RES-${String(item.id).padStart(3, '0')}</td>
                <td class="px-6 py-4 font-medium text-on-surface">${item.component_name}</td>
                <td class="px-6 py-4 text-on-surface-variant">${item.student_name} <span class="text-xs ml-1 bg-surface-container rounded px-1">${item.role}</span></td>
                <td class="px-6 py-4">${statusBadge}</td>
                <td class="px-6 py-4 text-right">${actionBtn}</td>
            </tr>
            `;
        });
    });
}

function returnItem(id){
    fetch("/api/return/"+id,{
        method:"POST"
    })
    .then(r=>r.json())
    .then(data=>{
        showToast(data.message, "success");
        loadDashboard();
        loadInventory();
        loadHistory();
    });
}

function showToast(message, type="success") {
    let container = document.getElementById("toast-container");
    if(!container) return;
    
    let toast = document.createElement("div");
    let bgColor = type === "success" ? "bg-secondary-container" : "bg-error-container";
    let textColor = type === "success" ? "text-on-secondary-container" : "text-on-error-container";
    let icon = type === "success" ? "check_circle" : "error";
    
    toast.className = `flex items-center gap-3 p-4 rounded-lg shadow-lg ${bgColor} ${textColor} transform transition-all duration-300 translate-x-full`;
    toast.innerHTML = `
        <span class="material-symbols-outlined">${icon}</span>
        <p class="font-medium text-sm">${message}</p>
    `;
    
    container.appendChild(toast);
    
    // animate in
    setTimeout(() => {
        toast.classList.remove('translate-x-full');
    }, 10);
    
    // remove after 3s
    setTimeout(() => {
        toast.classList.add('opacity-0');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}
