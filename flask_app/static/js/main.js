$(document).ready(function() {
    var isLoading = false;
    var projectId = $('#projectId').val(); // Read project ID from hidden input

    function showLoadingScreen() {
        if (!isLoading) {
            console.log('Showing loading screen');
            $('#loadingScreen').css('display', 'flex'); // Directly set the display property to flex
            isLoading = true;
        }
    }

    function hideLoadingScreen() {
        if (isLoading) {
            console.log('Hiding loading screen');
            $('#loadingScreen').css('display', 'none'); // Directly set the display property to none
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
                hideLoadingScreen(); // Hide loading screen once data is loaded
            },
            error: function(xhr, status, error) {
                console.error('Error loading equipment data:', error);
                hideLoadingScreen(); // Hide loading screen even if there's an error
            }
        });
    }

    var currentTab = $('#currentTab').val();
    if (currentTab === "") {
        currentTab = "Exchanger";
        $('#currentTab').val(currentTab);
    }
    loadEquipmentData(currentTab);

    $(document).on('click', '.equipment-type-tab', function(e) {
        e.preventDefault();
        var equipmentType = $(this).data('equipment-type');
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
                    if (response.length === 0) {
                        $('#currentRepairFields').hide();
                    } else {
                        var repair = response[0];
                        $('#currentRepairFields').show();
                        $('#currentRepairNumber').val(repair.repair_number);
                        $('#currentDescription').val(repair.description);
                        if (repair.file_path) {
                            $('#currentFileLink').attr('href', '/uploads/path:' + repair.file_path).show();
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
        var button = $(event.relatedTarget);
        var repairId = button.data('repair-id'); // Retrieve repair ID
        var componentId = button.data('component-id');
        var equipmentId = button.data('equipment-id');
        
        $.ajax({
            url: '/get_repair_details',
            type: 'GET',
            data: {
                repair_id: repairId // Use repair ID for specific repair details
            },
            success: function(response) {
                var container = $('#repairDetailsContainer');
                container.empty();  // Clear any existing content
                
                if (!response || response.length === 0) {
                    container.append('<p>No repairs found.</p>');
                } else {
                    var repair = response;
                    var repairEntry = `
                        <div class="repair-entry mb-3 p-3 border rounded">
                            <form id="repairStatusForm-${repair.id}" method="POST" class="border rounded" action="/repairs/update_repair_status/${repair.id}">
                                <div class="mb-3 p-2">
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
                                    ${repair.file_path ? `<a id="repairFileLink-${repair.id}" href="/uploads/path:${repair.file_path}" target="_blank" class="btn btn-warning">View Document</a>` : 'No document available'}
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
        formData.append('currentTab', currentTab);

        $.ajax({
            type: 'POST',
            url: $(this).attr('action'),
            data: formData,
            contentType: false,
            processData: false,
            success: function(response) {
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

