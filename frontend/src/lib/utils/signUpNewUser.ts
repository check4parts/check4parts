import { supabasePublicClient as supabase } from '$lib/utils/supabasePublicClient';

export async function signUpNewUser(email: string, password: string) {
	const { data, error } = await supabase.auth.signUp({
		email: email,
		password: password
	});
	console.log(data, error);
	return { data, error };
}
