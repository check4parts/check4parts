<script lang="ts">
	import { page } from '$app/state';
	let props = $props();
	$inspect({ props });

</script>

<section class="flex h-full w-full flex-col items-center justify-center">
	<h2 class="h3">Ой, щось пішло не так</h2>
	{page.error?.message}
</section>
