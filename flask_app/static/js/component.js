document.addEventListener('DOMContentLoaded', function () {
    var editComponentModal = new bootstrap.Modal(document.getElementById('editComponentModal'));
    var deleteConfirmationModal = new bootstrap.Modal(document.getElementById('deleteConfirmationModal'));

    document.querySelectorAll('.edit-button').forEach(function (button) {
        button.addEventListener('click', function () {
            var componentId = this.getAttribute('data-id');
            var componentName = this.getAttribute('data-name');

            document.getElementById('edit-id').value = componentId;
            document.getElementById('edit-name').value = componentName;

            document.getElementById('edit-component-form').action = '/component/edit_component/' + componentId;

            editComponentModal.show();
        });
    });

    document.getElementById('showDeleteConfirmation').addEventListener('click', function () {
        var componentId = document.getElementById('edit-id').value;
        var componentName = document.getElementById('edit-name').value;

        document.getElementById('delete-id').value = componentId;
        document.getElementById('delete-component-name').innerText = componentName;

        document.getElementById('delete-component-form').action = '/component/delete_component/' + componentId;

        editComponentModal.hide();
        deleteConfirmationModal.show();
    });

    // Retrieve the predetermined components from the hidden input
    var predeterminedComponents = JSON.parse(document.getElementById('predetermined-components').value);

    // Add new component field dynamically
    document.getElementById('add-component-field').addEventListener('click', function () {
        var newField = document.createElement('div');
        newField.className = 'form-group mt-3';

        var select = document.createElement('select');
        select.className = 'form-control mb-2';
        select.name = 'components[]';
        
        // Populate the select options with predetermined components
        predeterminedComponents.forEach(function(component) {
            var option = document.createElement('option');
            option.value = component;
            option.textContent = component;
            select.appendChild(option);
        });

        // Add custom option
        var customOption = document.createElement('option');
        customOption.value = 'other';
        customOption.textContent = 'Other';
        select.appendChild(customOption);

        newField.appendChild(select);

        var customInput = document.createElement('input');
        customInput.type = 'text';
        customInput.className = 'form-control mb-2 d-none';
        customInput.name = 'custom_components[]';
        customInput.placeholder = 'Enter component name';
        newField.appendChild(customInput);

        document.getElementById('component-fields').appendChild(newField);

        // Show custom input field if 'Custom' is selected
        select.addEventListener('change', function () {
            if (this.value === 'other') {
                customInput.classList.remove('d-none');
                customInput.required = true;
            } else {
                customInput.classList.add('d-none');
                customInput.required = false;
            }
        });
    });

    // Initial setup for the first select element
    document.querySelectorAll('select[name="components[]"]').forEach(function (select) {
        select.addEventListener('change', function () {
            var customInput = this.nextElementSibling;
            if (this.value === 'other') {
                customInput.classList.remove('d-none');
                customInput.required = true;
            } else {
                customInput.classList.add('d-none');
                customInput.required = false;
            }
        });
    });

    document.getElementById('add-component-form').addEventListener('submit', function (event) {
        event.preventDefault();
        var formData = new FormData(this);
        console.log('Form data:', Object.fromEntries(formData.entries()));

        var xhr = new XMLHttpRequest();
        xhr.open('POST', this.action, true);
        xhr.onload = function () {
            if (xhr.status === 200) {
                console.log('Components added successfully');
                window.location.reload();
            } else {
                console.error('Error adding components:', xhr.responseText);
            }
        };
        xhr.send(formData);
    });
});
