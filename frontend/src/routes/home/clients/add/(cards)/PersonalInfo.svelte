<script>
	import InputTextField from '$lib/components/inputs/card/InputTextField.svelte';

	let { missing = false } = $props();
</script>

<div class="card preset-filled-surface-50-950 flex flex-col p-8">
	<h3 class="h6">Персональна інформація</h3>
	<div class="flex flex-col gap-10">
		<InputTextField
			lable="Прізвище"
			type="text"
			name="last_name"
			placeholder="Введіть прізвище"
		/>
		<InputTextField
			lable="Ім'я"
			type="text"
			name="first_name"
			required
			placeholder="Введіть ім'я"
			{missing}
		/>
		<InputTextField
			lable="По батькові"
			type="text"
			name="middle_name"
			placeholder="Введіть по батькові"
		/>
		<InputTextField
			lable="Номер телефону"
			type="text"
			name="phone_number"
			placeholder="Введіть номер телефону"
			required
			{missing}
		/>
	</div>
</div>
