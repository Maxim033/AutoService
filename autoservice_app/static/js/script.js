class EmployeeFilter {
    constructor() {
        this.filters = {
            search: '',
            position: '',
            experience: '',
            schedule: '',
            availability: ''
        };
        this.init();
    }

    init() {
        // Обработчики для фильтров
        document.getElementById('searchInput').addEventListener('input', (e) => {
            this.filters.search = e.target.value;
            this.debouncedFilter();
        });

        document.getElementById('positionFilter').addEventListener('change', (e) => {
            this.filters.position = e.target.value;
            this.filterEmployees();
        });

        document.getElementById('experienceFilter').addEventListener('change', (e) => {
            this.filters.experience = e.target.value;
            this.filterEmployees();
        });

        document.getElementById('scheduleFilter').addEventListener('change', (e) => {
            this.filters.schedule = e.target.value;
            this.filterEmployees();
        });

        document.getElementById('availabilityFilter').addEventListener('change', (e) => {
            this.filters.availability = e.target.value;
            this.filterEmployees();
        });

        document.getElementById('resetFilters').addEventListener('click', () => {
            this.resetFilters();
        });

        // Инициализация выбранных чекбоксов
        this.initCheckboxes();

        // Инициализация tooltips
        this.initTooltips();
    }

    debouncedFilter() {
        clearTimeout(this.debounceTimer);
        this.debounceTimer = setTimeout(() => {
            this.filterEmployees();
        }, 300);
    }

    async filterEmployees() {
        const container = document.getElementById('employeesContainer');
        const countElement = document.getElementById('employeesCount');

        // Показываем индикатор загрузки
        container.classList.add('loading');

        try {
            const params = new URLSearchParams();
            if (this.filters.search) params.append('search', this.filters.search);
            if (this.filters.position) params.append('position', this.filters.position);
            if (this.filters.experience) params.append('experience', this.filters.experience);
            if (this.filters.schedule) params.append('schedule', this.filters.schedule);
            if (this.filters.availability) params.append('availability', this.filters.availability);

            const response = await fetch(`/api/employees/filter?${params}`);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();

            // Проверяем, есть ли ошибка в ответе
            if (data.error) {
                throw new Error(data.error);
            }

            // Сохраняем выбранные чекбоксы
            const selectedEmployees = this.getSelectedEmployees();

            // Обновляем контейнер
            container.innerHTML = this.renderEmployees(data.employees);
            countElement.textContent = `Найдено сотрудников: ${data.count}`;

            // Восстанавливаем выбранные чекбоксы
            this.restoreSelectedEmployees(selectedEmployees);

            // Переинициализируем tooltips
            this.initTooltips();

        } catch (error) {
            console.error('Ошибка фильтрации:', error);
            container.innerHTML = `
                <div class="alert alert-danger">
                    <i class="bi bi-exclamation-triangle"></i>
                    Ошибка загрузки сотрудников: ${this.sanitizeInput(error.message)}
                </div>
            `;
        } finally {
            container.classList.remove('loading');
        }
    }

    renderEmployees(employees) {
        if (employees.length === 0) {
            return `
                <div class="alert alert-warning">
                    <i class="bi bi-exclamation-triangle"></i>
                    Сотрудники не найдены по заданным фильтрам.
                </div>
            `;
        }

        return `
            <div class="row">
                ${employees.map(emp => `
                    <div class="col-md-4 mb-2">
                        <div class="card employee-card ${emp.availability === 'busy' ? 'border-warning' : ''}">
                            <div class="card-body p-2">
                                <div class="form-check">
                                    <input class="form-check-input employee-checkbox"
                                           type="checkbox"
                                           name="employee_ids"
                                           value="${emp.id}"
                                           id="emp_${emp.id}"
                                           ${emp.availability === 'busy' ? 'data-bs-toggle="tooltip" data-bs-title="Занят многими ремонтами"' : ''}>
                                    <label class="form-check-label w-100" for="emp_${emp.id}">
                                        <div class="fw-bold">${this.sanitizeInput(emp.full_name)}</div>
                                        <div class="small text-muted">
                                            <div>${this.sanitizeInput(emp.position)}</div>
                                            <div>Стаж: ${emp.experience} лет</div>
                                            <div>График: ${this.sanitizeInput(emp.schedule)}</div>
                                            <div class="text-success">З/п: ${this.sanitizeInput(emp.formatted_salary)}</div>
                                            <div class="${emp.availability === 'busy' ? 'availability-busy' : 'availability-free'}">
                                                🛠️ Активных ремонтов: ${emp.active_repairs_count}
                                                ${emp.availability === 'busy' ? ' 🔥' : ' ✅'}
                                            </div>
                                        </div>
                                    </label>
                                </div>
                            </div>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    }

    getSelectedEmployees() {
        const checkboxes = document.querySelectorAll('.employee-checkbox:checked');
        return Array.from(checkboxes).map(cb => cb.value);
    }

    restoreSelectedEmployees(selectedIds) {
        selectedIds.forEach(id => {
            const checkbox = document.querySelector(`.employee-checkbox[value="${id}"]`);
            if (checkbox) {
                checkbox.checked = true;
                checkbox.closest('.employee-card').classList.add('selected');
            }
        });
    }

    initCheckboxes() {
        // Делегирование событий для чекбоксов
        document.getElementById('employeesContainer').addEventListener('change', (e) => {
            if (e.target.classList.contains('employee-checkbox')) {
                const card = e.target.closest('.employee-card');
                if (e.target.checked) {
                    card.classList.add('selected');
                } else {
                    card.classList.remove('selected');
                }
            }
        });
    }

    initTooltips() {
        // Инициализация Bootstrap tooltips
        const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
        const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
    }

    resetFilters() {
        // Сбрасываем значения фильтров
        document.getElementById('searchInput').value = '';
        document.getElementById('positionFilter').value = '';
        document.getElementById('experienceFilter').value = '';
        document.getElementById('scheduleFilter').value = '';
        document.getElementById('availabilityFilter').value = '';

        this.filters = {
            search: '',
            position: '',
            experience: '',
            schedule: '',
            availability: ''
        };

        this.filterEmployees();
    }

    sanitizeInput(input) {
        // Базовая защита от XSS на клиенте
        const div = document.createElement('div');
        div.textContent = input;
        return div.innerHTML;
    }
}

// Защита от XSS - санация ввода
function sanitizeInput(input) {
    const div = document.createElement('div');
    div.textContent = input;
    return div.innerHTML;
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    new EmployeeFilter();

    // Защита от CSRF - добавление токена к формам
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        if (form.method.toLowerCase() === 'post') {
            const csrfToken = document.querySelector('meta[name="csrf-token"]');
            if (csrfToken) {
                const input = document.createElement('input');
                input.type = 'hidden';
                input.name = 'csrf_token';
                input.value = csrfToken.content;
                form.appendChild(input);
            }
        }
    });

    // Защита от внедрения кода в текстовые поля
    const textareas = document.querySelectorAll('textarea, input[type="text"]');
    textareas.forEach(field => {
        field.addEventListener('input', function(e) {
            // Базовая защита - удаляем опасные конструкции
            let value = e.target.value;
            value = value.replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '');
            value = value.replace(/javascript:/gi, '');
            value = value.replace(/on\w+=/gi, '');
            e.target.value = value;
        });
    });

    // Обработка вкладок для сохранения состояния
    const repairTabs = document.getElementById('repairsTabs');
    if (repairTabs) {
        repairTabs.addEventListener('shown.bs.tab', function (e) {
            // Сохраняем активную вкладку в sessionStorage
            sessionStorage.setItem('activeRepairTab', e.target.getAttribute('id'));
        });

        // Восстанавливаем активную вкладку при загрузке
        const activeTab = sessionStorage.getItem('activeRepairTab');
        if (activeTab) {
            const tabElement = document.getElementById(activeTab);
            if (tabElement) {
                new bootstrap.Tab(tabElement).show();
            }
        }
    }
});

// Функция для обновления информации о ремонте
function updateRepairInfo(repairId) {
    const repairInfo = document.getElementById('repairInfo');
    const repairDetails = document.getElementById('repairDetails');

    if (!repairId) {
        repairInfo.style.display = 'none';
        return;
    }

    // Получаем информацию из data-атрибутов выбранного option
    const selectedOption = document.querySelector(`#repair_id option[value="${repairId}"]`);
    if (selectedOption) {
        const description = selectedOption.getAttribute('data-description');
        const car = selectedOption.getAttribute('data-car');
        const cost = selectedOption.getAttribute('data-cost');

        repairDetails.innerHTML = `
            <div><strong>Автомобиль:</strong> ${sanitizeInput(car)}</div>
            <div><strong>Описание:</strong> ${sanitizeInput(description)}</div>
            <div><strong>Стоимость работ:</strong> ${parseFloat(cost || 0).toLocaleString('ru-RU')} ₽</div>
        `;
        repairInfo.style.display = 'block';
    }
}

// Глобальные функции для использования в HTML
window.updateRepairInfo = updateRepairInfo;
window.sanitizeInput = sanitizeInput;