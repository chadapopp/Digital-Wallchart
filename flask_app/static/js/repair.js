console.log('repair.js loaded');
console.lo
document.addEventListener("DOMContentLoaded", function() {
    console.log('DOM fully loaded and parsed'); // Debugging log

    $('#repairModal').on('show.bs.modal', function(event) {
        var button = $(event.relatedTarget);
        var componentId = button.data('component-id');
        var equipmentId = button.data('equipment-id');
        
        console.log('Fetching repair details for component:', componentId, 'and equipment:', equipmentId); // Debugging log

        $.ajax({
            url: '/get_repair_details',
            type: 'GET',
            data: {
                component_id: componentId,
                equipment_id: equipmentId
            },
            success: function(response) {
                console.log('Received repair details:', response); // Debugging log

                var container = $('#repairDetailsContainer');
                container.empty();  // Clear any existing content
                
                if (response.length === 0) {
                    container.append('<p>No repairs found.</p>');
                } else {
                    response.forEach(function(repair) {
                        var repairEntry = `
                            <div class="repair-entry mb-3 p-3 border rounded">
                                <form id="repairStatusForm-${repair.id}" method="POST" action="/repairs/update_repair_status/${repair.id}">
                                    <div class="mb-3">
                                        <label for="repairStatus-${repair.id}" class="form-label">Status</label>
                                        <select class="form-select" id="repairStatus-${repair.id}" name="status">
                                            <option value="In Progress" ${repair.repair_status === 'In Progress' ? 'selected' : ''}>In Progress</option>
                                            <option value="Complete" ${repair.repair_status === 'Complete' ? 'selected' : ''}>Complete</option>
                                            <option value="Rejected" ${repair.repair_status === 'Rejected' ? 'selected' : ''}>Rejected</option>
                                            <option value="Deferred" ${repair.repair_status === 'Deferred' ? 'selected' : ''}>Deferred</option>
                                        </select>
                                    </div>
                                    <div class="mb-3">
                                        <label for="repairDescription-${repair.id}" class="form-label">Description</label>
                                        <textarea class="form-control" id="repairDescription-${repair.id}" name="description" rows="3" readonly>${repair.description}</textarea>
                                    </div>
                                    <div class="mb-3">
                                        <label for="repairDocument-${repair.id}" class="form-label">Repair Document</label>
                                        <a id="repairFileLink-${repair.id}" href="/uploads/${repair.file_path}" target="_blank">View Document</a>
                                    </div>
                                    <button type="submit" class="btn btn-primary">Update Status</button>
                                </form>
                            </div>
                        `;
                        container.append(repairEntry);
                    });
                }
            },
            error: function(xhr, status, error) {
                console.error('Error fetching repair details:', error);
            }
        });
    });
});
