<script lang="ts">
	import InputTextField from '$lib/components/inputs/card/InputTextField.svelte';

	let cars = $state([{ name: '', vinCode: '', plate: '' }]);

	let currentCarIndex = $state(0);

	function nextCar() {
		if (currentCarIndex < cars.length - 1) {
			currentCarIndex++;
		}
	}

	function prevCar() {
		if (currentCarIndex > 0) {
			currentCarIndex--;
		}
	}

	function addCar() {
		cars.push({ name: '', vinCode: '', plate: '' });
		currentCarIndex = cars.length - 1;
	}

	function removeCar() {
		if (cars.length > 1) {
			cars.splice(currentCarIndex, 1);
			if (currentCarIndex >= cars.length) {
				currentCarIndex = cars.length - 1;
			}
			cars = cars;
		}
	}
</script>

{#each cars as car, index }
    {#if index != currentCarIndex}
        <input type="hidden" required name={`cars[${index}][name]`} value={car.name} />
        <input type="hidden" name={`cars[${index}][vinCode]`} value={car.vinCode} />
        <input type="hidden" required name={`cars[${index}][plate]`} value={car.plate} />
    {/if}
{/each}

<div class="card preset-filled-surface-50-950 flex flex-col justify-between p-8">
	<h3 class="h6">Інформацію про автомобіль</h3>
	<div class="flex flex-col gap-10">
		<InputTextField
			lable="Назва"
			name={`cars[${currentCarIndex}][name]`}
			bind:value={cars[currentCarIndex].name}
			placeholder="Volkswagen Passat"
		/>
		<InputTextField
			lable="VIN-код"
			name={`cars[${currentCarIndex}][vinCode]`}
			bind:value={cars[currentCarIndex].vinCode}
			placeholder="WVWZZZ3CZEE123456"
		/>
		<InputTextField
			lable="Номерний знак"
			name={`cars[${currentCarIndex}][plate]`}
			bind:value={cars[currentCarIndex].plate}
			placeholder="CA9012OP"
		/>
	</div>

	<div class="mt-6 flex items-center justify-between">
		<div class="flex flex-row gap-5">
			<div class="flex items-center gap-4 bg-white p-1 rounded-3xl">
				<button
					type="button"
					onclick={prevCar}
					disabled={currentCarIndex === 0}
					class="text-gray-600 transition-colors hover:text-gray-900 disabled:text-gray-300"
					aria-label="Попередній автомобіль"
				>
					<svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M15 19l-7-7 7-7"
						/>
					</svg>
				</button>

				<span class="text-sm w-10 text-center">
					{currentCarIndex + 1}/{cars.length}
				</span>

				<button
					type="button"
					onclick={nextCar}
					disabled={currentCarIndex === cars.length - 1}
					class="text-gray-600 transition-colors hover:text-gray-900 disabled:text-gray-300"
					aria-label="Наступний автомобіль"
				>
					<svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M9 5l7 7-7 7"
						/>
					</svg>
				</button>
			</div>
			{#if cars.length > 1}
				<button
					type="button"
					onclick={removeCar}
					aria-label="Видалити"
					class="btn-icon text-surface-500"
				>
					<i class="fa-solid fa-trash-can"></i>
				</button>
			{/if}
		</div>
		<div class="flex flex-row gap-5">
			<button type="button" onclick={addCar} class="btn">
				<svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M12 4v16m8-8H4"
					/>
				</svg>
				<span>Додати автомобіль</span>
			</button>
		</div>
	</div>
</div>
