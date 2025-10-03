<script lang="ts">
	let name = $state('');
	let email = $state('');
	let message = $state('');
	let isSubmitting = $state(false);
	let error = $state('');
</script>

<section class="container mx-auto py-16">
	<div class="bg-primary-950 text-surface-50 mx-auto max-w-6xl rounded-3xl p-12">
		<div class="flex flex-col gap-8 lg:flex-row">
			<!-- Ліва частина: заголовок та опис -->
			<div class="lg:w-1/2">
				<h2 class="mb-4 text-3xl font-bold">Зв’яжіться з нами</h2>
				<p >
					Звертайтеся до нас у будь-який час. Ми зв’яжемося з вами як тільки зможемо!
				</p>
			</div>

			<form class="flex flex-col gap-4 lg:w-1/2">
				<div>
					<label for="name" class="mb-1 block text-sm">Ім’я</label>
					<input
						id="name"
						type="text"
						bind:value={name}
						placeholder="Ваше ім’я"
						class="border-surface-50 placeholder:text-surface-50/80 focus:ring-primary-600 w-full rounded-lg border bg-transparent px-4 py-2 focus:outline-none focus:ring-2"
					/>
				</div>

				<div>
					<label for="email" class="mb-1 block text-sm">Електронна пошта</label>
					<input
						id="email"
						type="email"
						bind:value={email}
						placeholder="example@mail.com"
						class="border-surface-50 placeholder:text-surface-50/80 focus:ring-primary-600 w-full rounded-lg border bg-transparent px-4 py-2 focus:outline-none focus:ring-2"
					/>
				</div>

				<div>
					<label for="message" class="mb-1 block text-sm">Повідомлення</label>
					<textarea
						id="message"
						rows="5"
						bind:value={message}
						placeholder="Ваше повідомлення…"
						class="border-surface-50 placeholder:text-surface-50/80 focus:ring-primary-600 w-full resize-none rounded-lg border bg-transparent px-4 py-2 focus:outline-none focus:ring-2"
					></textarea>
				</div>

				{#if error}
					<p class="text-sm text-red-400">{error}</p>
				{/if}

				<button
					type="submit"
					class="bg-surface-50 text-primary-950 mt-2 self-end rounded-lg px-6 py-2 font-semibold hover:bg-white disabled:opacity-50"
					disabled={isSubmitting}
				>
					{#if isSubmitting}
						Надсилаємо…
					{:else}
						Надіслати
					{/if}
				</button>
			</form>
		</div>
	</div>
</section>
