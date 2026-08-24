import os
import re
import shutil

# 1. Read stitch_ui.html
with open('stitch_ui.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Add Jinja tag for script
html = html.replace('</body></html>', '<script src="{{ url_for(\'static\', filename=\'script.js\') }}"></script>\n<div id="toast-container" class="fixed top-4 right-4 z-50 flex flex-col gap-2"></div>\n</body>\n</html>')

# Add IDs to KPI metrics
html = html.replace('<span class="text-2xl font-bold font-mono text-on-surface">10</span>', '<span class="text-2xl font-bold font-mono text-on-surface" id="totalItems">10</span>')
html = html.replace('<span class="text-2xl font-bold font-mono text-on-surface">133</span>', '<span class="text-2xl font-bold font-mono text-on-surface" id="availableItems">133</span>')
html = html.replace('<span class="text-2xl font-bold font-mono text-on-surface">6</span>', '<span class="text-2xl font-bold font-mono text-on-surface" id="reservedItems">6</span>')
html = html.replace('<span class="text-2xl font-bold font-mono text-on-surface">2</span>', '<span class="text-2xl font-bold font-mono text-on-surface" id="users">2</span>')

# Add ID to search box
html = html.replace('placeholder="Search components..." type="text"/>', 'placeholder="Search components..." type="text" id="searchBox" onkeyup="searchInventory()"/>')

# Add Student Name and Role next to search box
search_div = '''<div class="relative">
<span class="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant text-sm" data-icon="search">search</span>
<input class="pl-9 pr-4 py-2 border border-outline-variant rounded-lg text-sm focus:ring-2 focus:ring-primary-container focus:border-primary-container bg-surface-bright w-full md:w-64" placeholder="Search components..." type="text" id="searchBox" onkeyup="searchInventory()"/>
</div>'''

new_inputs = '''
<div class="flex gap-2">
    <input type="text" id="studentName" placeholder="Student Name" class="px-4 py-2 border border-outline-variant rounded-lg text-sm focus:ring-2 focus:ring-primary-container focus:border-primary-container bg-surface-bright w-32 md:w-48">
    <select id="role" class="px-4 py-2 border border-outline-variant rounded-lg text-sm focus:ring-2 focus:ring-primary-container focus:border-primary-container bg-surface-bright">
        <option>Student</option>
        <option>Faculty</option>
        <option>Lab Assistant</option>
    </select>
</div>
'''
html = html.replace(search_div, new_inputs + '\n' + search_div)

# Clear hardcoded inventory cards and add ID to grid
grid_start = '<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">'
grid_end = '<!-- Active Checkouts Table -->'
import re
grid_pattern = re.compile(re.escape(grid_start) + r'.*?(?=<!-- Active Checkouts Table -->)', re.DOTALL)
html = grid_pattern.sub('<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6" id="inventory-grid">\n</div>\n</section>\n', html)

# Clear hardcoded active checkouts and add ID to tbody
tbody_start = '<tbody class="divide-y divide-outline-variant bg-surface">'
tbody_pattern = re.compile(re.escape(tbody_start) + r'.*?</tbody>', re.DOTALL)
html = tbody_pattern.sub('<tbody class="divide-y divide-outline-variant bg-surface" id="history-tbody">\n</tbody>', html)

# Add Reserve Modal HTML
modal_html = """
<div id="reserveModal" class="fixed inset-0 bg-black/50 z-[100] hidden flex items-center justify-center backdrop-blur-sm">
    <div class="bg-surface rounded-xl shadow-xl border border-outline-variant w-full max-w-md p-6">
        <h3 class="text-xl font-bold text-on-surface mb-4">Reserve Equipment</h3>
        <div class="mb-4">
            <p class="text-sm text-on-surface-variant font-medium">Equipment</p>
            <p class="text-lg font-bold text-on-surface" id="modalEquipmentName">-</p>
            <p class="text-xs font-mono text-on-surface-variant" id="modalEquipmentId">-</p>
        </div>
        <div class="mb-6">
            <p class="text-sm text-on-surface-variant font-medium mb-1">Availability</p>
            <p class="font-mono text-primary font-bold" id="modalAvailability">-</p>
        </div>
        <div class="flex justify-end gap-3 mt-6">
            <button onclick="closeModal()" class="px-4 py-2 border border-outline-variant text-on-surface-variant rounded-lg text-sm font-medium hover:bg-surface-container transition-colors">Cancel</button>
            <button onclick="confirmReservation()" class="px-4 py-2 bg-primary text-on-primary rounded-lg text-sm font-semibold hover:bg-[#005a6a] transition-colors shadow-sm">Confirm Reservation</button>
        </div>
    </div>
</div>
"""
html = html.replace('</body></html>', modal_html + '\n</body></html>')

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Updated index.html")
