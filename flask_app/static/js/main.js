$(document).ready(function() {
    console.log('Main script loaded'); // Debugging log

    var isLoading = false;
    var projectId = $('#projectId').val(); // Read project ID from hidden input

    function showLoadingScreen() {
        if (!isLoading) {
            $('#loadingScreen').show();
            isLoading = true;
        }
    }

    function hideLoadingScreen() {
        if (isLoading) {
            $('#loadingScreen').hide();
            isLoading = false;
        }
    }

    function loadEquipmentData(equipmentType) {
        console.log('Loading equipment data for type:', equipmentType); // Logging
        showLoadingScreen();
        $.ajax({
            url: '/view_wallchart/' + projectId + '?equipment_type=' + equipmentType, // Use project ID
            type: 'GET',
            success: function(response) {
                console.log('Equipment data loaded successfully'); // Logging
                $('#equipmentTabContent').html(response);
                hideLoadingScreen();
            },
            error: function(xhr, status, error) {
                console.error('Error loading equipment data:', error); // Logging
                hideLoadingScreen();
            }
        });
    }

    var currentTab = $('#currentTab').val();
    console.log('Initial currentTab value:', currentTab); // Logging
    if (currentTab === "") {
        currentTab = "Exchanger";
        $('#currentTab').val(currentTab);
    }
    console.log('CurrentTab after check:', currentTab); // Logging
    loadEquipmentData(currentTab);

    $(document).on('click', '.equipment-type-tab', function(e) {
        e.preventDefault();
        var equipmentType = $(this).data('equipment-type');
        console.log('Tab clicked, equipment type:', equipmentType); // Logging
        $('#currentTab').val(equipmentType); // Update the hidden input value
        loadEquipmentData(equipmentType);

        // Remove 'active' class from all tabs and add to the clicked tab
        $('.equipment-type-tab').removeClass('active');
        $(this).addClass('active');
    });

    $(document).on('show.bs.modal', '#methodModal', function(event) {
        var button = $(event.relatedTarget);
        var methodId = button.data('method-id');
        var componentId = button.data('component-id');
        var methodStatus = button.data('method-status');
        var equipmentId = button.data('equipment-id');

        console.log('Showing method modal for method:', methodId, 'component:', componentId); // Debugging log

        var modal = $(this);
        modal.find('#methodId').val(methodId);
        modal.find('#componentId').val(componentId);
        modal.find('#equipmentId').val(equipmentId);
        modal.find('#methodStatus').val(methodStatus);

        if (methodStatus === 'Repair Required') {
            $('#repairFields').show();

            $.ajax({
                url: '/get_repair_details',
                type: 'GET',
                data: {
                    component_id: componentId,
                    method_id: methodId,
                    equipment_id: equipmentId
                },
                success: function(response) {
                    console.log('Received repair details:', response); // Debugging log

                    if (response.length === 0) {
                        $('#currentRepairFields').hide();
                    } else {
                        var repair = response[0];
                        $('#currentRepairFields').show();
                        $('#currentRepairNumber').val(repair.repair_number);
                        $('#currentDescription').val(repair.description);
                        if (repair.file_path) {
                            $('#currentFileLink').attr('href', '/uploads/' + repair.file_path).show();
                        } else {
                            $('#currentFileLink').hide();
                        }
                    }
                },
                error: function(xhr, status, error) {
                    console.error('Error fetching repair details:', error);
                }
            });

        } else {
            $('#repairFields').hide();
            $('#currentRepairFields').hide();
        }
    });

    $(document).on('show.bs.modal', '#repairModal', function(event) {
        console.log('repairModal show.bs.modal event triggered'); // Debugging log
        var button = $(event.relatedTarget);
        var repairId = button.data('repair-id'); // Retrieve repair ID
        var componentId = button.data('component-id');
        var equipmentId = button.data('equipment-id');
        
        console.log('Fetching repair details for repair:', repairId); // Debugging log

        $.ajax({
            url: '/get_repair_details',
            type: 'GET',
            data: {
                repair_id: repairId // Use repair ID for specific repair details
            },
            success: function(response) {
                console.log('Received repair details:', response); // Debugging log

                var container = $('#repairDetailsContainer');
                container.empty();  // Clear any existing content
                
                if (!response || response.length === 0) {
                    container.append('<p>No repairs found.</p>');
                } else {
                    var repair = response;
                    var repairEntry = `
                        <div class="repair-entry mb-3 p-3 border rounded">
                            <form id="repairStatusForm-${repair.id}" method="POST" action="/repairs/update_repair_status/${repair.id}">
                                <div class="mb-3">
                                    <label for="repairStatus-${repair.id}" class="form-label">Status</label>
                                    <select class="form-select" id="repairStatus-${repair.id}" name="status">
                                        <option value="Repair Required" ${repair.repair_status === 'Repair Required' ? 'selected' : ''}>Repair Required</option>
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
                }
            },
            error: function(xhr, status, error) {
                console.error('Error fetching repair details:', error);
            }
        });
    });

    $(document).on('submit', '#methodStatusForm', function(event) {
        event.preventDefault();
        showLoadingScreen();
        $('#methodModal').modal('hide');

        var formData = new FormData(this);
        var currentTab = $('#currentTab').val();
        console.log('Form submitted, currentTab:', currentTab); // Logging
        formData.append('currentTab', currentTab);

        $.ajax({
            type: 'POST',
            url: $(this).attr('action'),
            data: formData,
            contentType: false,
            processData: false,
            success: function(response) {
                console.log('Method status updated, reloading tab:', response.currentTab); // Logging
                var newTab = response.currentTab || currentTab; // Default to currentTab if empty
                $('#currentTab').val(newTab);
                loadEquipmentData(newTab);
                // Remove 'active' class from all tabs and add to the clicked tab
                $('.equipment-type-tab').removeClass('active');
                $('a[data-equipment-type="' + newTab + '"]').addClass('active');
                hideLoadingScreen();
            },
            error: function(xhr, status, error) {
                console.log('Error updating method status:', error);
                hideLoadingScreen();
            }
        });
    });

    $(document).on('change', '#methodStatus', function() {
        if ($(this).val() === 'Repair Required') {
            $('#repairFields').show();
        } else {
            $('#repairFields').hide();
        }
    });
});
