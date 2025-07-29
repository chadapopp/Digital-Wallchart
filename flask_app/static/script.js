
var $ = jQuery.noConflict();
$(document).ready(function() {
    // Your jQuery code here
    $(document).ready(function() {
        // Add event listener for tab clicks
        $('.equipment-type-tab').on('click', function(e) {
            e.preventDefault(); // Prevent the default behavior of following the link
            var equipmentType = $(this).data('equipment-type'); // Get the equipment type from data attribute
            loadEquipmentData(equipmentType); // Call function to load equipment data when a tab is clicked
            $('#wallchart-header').hide(); // Hide the header
        });
    
        // Function to load equipment data
        function loadEquipmentData(equipmentType) {
            // Send AJAX request to fetch equipment data based on equipment type
            $.ajax({
                url: '/view_wallchart/{{ project.id }}?equipment_type=' + equipmentType, // Pass equipment type as query parameter
                type: 'GET',
                success: function(response) {
                    // Update the tab content with the fetched equipment data
                    $('#equipmentTabContent').html(response);
                },
                error: function(xhr, status, error) {
                    console.error(error);
                }
            });
        }
    });
});
