<script lang="ts">
</script>

{#snippet inputTextField(
	lable: string,
	type: string,
	name: string,
	placeholder: string,
	required: boolean = false
)}
	<label class="label">
		<span class="text-sm">{lable}</span>
		<input
			class="input focus:outline-primary-500 h-12 bg-white placeholder:text-gray-400"
			style="box-shadow: none;"
			{name}
			{type}
			{placeholder}
			{required}
		/>
	</label>
{/snippet}

<header class="flex items-center justify-between">
	<h2 class="h3">Додавання користувача</h2>
</header>

<section class="m-5">
	<form action="?/add" method="post">
		<div class="grid grid-cols-2 grid-rows-[1fr_0.5fr] gap-5">
			<div class="card preset-filled-surface-50-950 flex w-full flex-col p-8">
				<h3 class="h6">Персональна інформація</h3>
				<div class="flex flex-col gap-10">
					{@render inputTextField('Прізвище', 'text', 'name', 'Введіть прізвище')}
					{@render inputTextField("Ім'я", 'text', 'first_name', "Введіть ім'я")}
					{@render inputTextField('По батькові', 'text', 'last_name', 'Введіть по батькові')}
				</div>
			</div>

      <div class="card preset-filled-surface-50-950 flex w-full flex-col p-8 col-start-1 row-start-2">
				<h3 class="h6">Контактні дані</h3>
				<div class="flex flex-col gap-10">
					{@render inputTextField('Номір телефону', 'text', 'name', 'Введіть прізвище')}
					{@render inputTextField('Адреса місця роботи', 'text', 'first_name', "Введіть ім'я")}
				</div>
			</div>

			<div class="card preset-filled-surface-50-950 flex w-full flex-col p-8 col-start-2 row-start-1">
				<h3 class="h6">Дані для входу</h3>
				<div class="flex flex-col gap-10">
					{@render inputTextField('Електронна пошта', 'email', 'eamil', 'Введіть адресу  електронної пошти')}
					{@render inputTextField("Пароль", 'password', 'password', "Введіть пароль")}
					{@render inputTextField('Повторіть пароль', 'password', 'repeat_password', 'Повторіть пароль')}
				</div>
			</div>



      <div class="h-full flex flex-col justify-between row-start-2">
        <div class="card preset-filled-surface-50-950 flex w-full flex-col p-8">
          <h3 class="h6">Роль у системі</h3>
          <div class="flex flex-col gap-10">
            {@render inputTextField('Посада', 'text', 'name', 'Обреіть посаду користувача')}
          </div>
        </div>
        <div class="flex justify-end gap-5">
          <a class="btn preset-outlined-primary-950-50 mt-5 w-[10rem]" href="/home/settings/users">Скасувати</a>
          <button class="btn preset-filled-primary-950-50 mt-5 w-[10rem]" type="submit">
            Додати
          </button>
        </div>
      </div>
		</div>
	</form>
</section>
