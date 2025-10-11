export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export type Database = {
  // Allows to automatically instantiate createClient with right options
  // instead of createClient<Database, { PostgrestVersion: 'XX' }>(URL, KEY)
  __InternalSupabase: {
    PostgrestVersion: "12.2.3 (519615d)"
  }
  public: {
    Tables: {
      cars: {
        Row: {
          client_id: string | null
          id: number
          license_plate: string | null
          name: string | null
          vin_code: string | null
        }
        Insert: {
          client_id?: string | null
          id?: number
          license_plate?: string | null
          name?: string | null
          vin_code?: string | null
        }
        Update: {
          client_id?: string | null
          id?: number
          license_plate?: string | null
          name?: string | null
          vin_code?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "cars_client_id_fkey"
            columns: ["client_id"]
            isOneToOne: false
            referencedRelation: "clients"
            referencedColumns: ["id"]
          },
        ]
      }
      client_types: {
        Row: {
          id: number
          name: string | null
        }
        Insert: {
          id?: number
          name?: string | null
        }
        Update: {
          id?: number
          name?: string | null
        }
        Relationships: []
      }
      clients: {
        Row: {
          address: string | null
          company_id: string | null
          first_name: string | null
          id: string
          last_name: string | null
          middle_name: string | null
          note: string | null
          phone_number: string | null
          type_id: number | null
        }
        Insert: {
          address?: string | null
          company_id?: string | null
          first_name?: string | null
          id?: string
          last_name?: string | null
          middle_name?: string | null
          note?: string | null
          phone_number?: string | null
          type_id?: number | null
        }
        Update: {
          address?: string | null
          company_id?: string | null
          first_name?: string | null
          id?: string
          last_name?: string | null
          middle_name?: string | null
          note?: string | null
          phone_number?: string | null
          type_id?: number | null
        }
        Relationships: [
          {
            foreignKeyName: "clients_company_id_fkey"
            columns: ["company_id"]
            isOneToOne: false
            referencedRelation: "companies"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "clients_type_id_fkey"
            columns: ["type_id"]
            isOneToOne: false
            referencedRelation: "client_types"
            referencedColumns: ["id"]
          },
        ]
      }
      companies: {
        Row: {
          city: string | null
          id: string
          name: string | null
          region: string | null
        }
        Insert: {
          city?: string | null
          id?: string
          name?: string | null
          region?: string | null
        }
        Update: {
          city?: string | null
          id?: string
          name?: string | null
          region?: string | null
        }
        Relationships: []
      }
      companies_to_approve: {
        Row: {
          city: string | null
          company_name: string | null
          created_at: string
          email: string | null
          first_name: string | null
          id: number
          last_name: string | null
          middle_name: string | null
          phone: string | null
          region: string | null
          street: string | null
        }
        Insert: {
          city?: string | null
          company_name?: string | null
          created_at?: string
          email?: string | null
          first_name?: string | null
          id?: number
          last_name?: string | null
          middle_name?: string | null
          phone?: string | null
          region?: string | null
          street?: string | null
        }
        Update: {
          city?: string | null
          company_name?: string | null
          created_at?: string
          email?: string | null
          first_name?: string | null
          id?: number
          last_name?: string | null
          middle_name?: string | null
          phone?: string | null
          region?: string | null
          street?: string | null
        }
        Relationships: []
      }
      company_provider: {
        Row: {
          access_data: Json | null
          company_id: string | null
          data: Json
          id: string
          provider_id: string | null
          state: string
        }
        Insert: {
          access_data?: Json | null
          company_id?: string | null
          data?: Json
          id?: string
          provider_id?: string | null
          state?: string
        }
        Update: {
          access_data?: Json | null
          company_id?: string | null
          data?: Json
          id?: string
          provider_id?: string | null
          state?: string
        }
        Relationships: [
          {
            foreignKeyName: "company_provider_company_id_fkey"
            columns: ["company_id"]
            isOneToOne: false
            referencedRelation: "companies"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "company_provider_provider_id_fkey"
            columns: ["provider_id"]
            isOneToOne: false
            referencedRelation: "providers"
            referencedColumns: ["id"]
          },
        ]
      }
      providers: {
        Row: {
          access_props: Json | null
          adapter: string | null
          api_url: string | null
          data_props: Json
          id: string
          logo_url: string | null
          name: string
          short_name: string | null
        }
        Insert: {
          access_props?: Json | null
          adapter?: string | null
          api_url?: string | null
          data_props?: Json
          id?: string
          logo_url?: string | null
          name: string
          short_name?: string | null
        }
        Update: {
          access_props?: Json | null
          adapter?: string | null
          api_url?: string | null
          data_props?: Json
          id?: string
          logo_url?: string | null
          name?: string
          short_name?: string | null
        }
        Relationships: []
      }
      roles: {
        Row: {
          id: string
          name: string | null
          permisions: string | null
        }
        Insert: {
          id?: string
          name?: string | null
          permisions?: string | null
        }
        Update: {
          id?: string
          name?: string | null
          permisions?: string | null
        }
        Relationships: []
      }
      staff: {
        Row: {
          comments: string | null
          company_id: string
          contacts: Json | null
          created_at: string
          email: string | null
          first_name: string | null
          id: string
          last_name: string | null
          middle_name: string | null
          phone_number: string | null
          role_id: string
          trading_point_id: string | null
          user_id: string | null
        }
        Insert: {
          comments?: string | null
          company_id?: string
          contacts?: Json | null
          created_at?: string
          email?: string | null
          first_name?: string | null
          id?: string
          last_name?: string | null
          middle_name?: string | null
          phone_number?: string | null
          role_id: string
          trading_point_id?: string | null
          user_id?: string | null
        }
        Update: {
          comments?: string | null
          company_id?: string
          contacts?: Json | null
          created_at?: string
          email?: string | null
          first_name?: string | null
          id?: string
          last_name?: string | null
          middle_name?: string | null
          phone_number?: string | null
          role_id?: string
          trading_point_id?: string | null
          user_id?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "staff_company_id_fkey"
            columns: ["company_id"]
            isOneToOne: false
            referencedRelation: "companies"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "staff_role_id_fkey"
            columns: ["role_id"]
            isOneToOne: false
            referencedRelation: "roles"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "staff_trading_point_id_fkey"
            columns: ["trading_point_id"]
            isOneToOne: false
            referencedRelation: "trading_points"
            referencedColumns: ["id"]
          },
        ]
      }
      trading_points: {
        Row: {
          company_id: string | null
          created_at: string
          id: string
          locality: string | null
          name: string | null
          region: string | null
          street: string | null
        }
        Insert: {
          company_id?: string | null
          created_at?: string
          id?: string
          locality?: string | null
          name?: string | null
          region?: string | null
          street?: string | null
        }
        Update: {
          company_id?: string | null
          created_at?: string
          id?: string
          locality?: string | null
          name?: string | null
          region?: string | null
          street?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "trading_points_company_id_fkey"
            columns: ["company_id"]
            isOneToOne: false
            referencedRelation: "companies"
            referencedColumns: ["id"]
          },
        ]
      }
    }
    Views: {
      [_ in never]: never
    }
    Functions: {
      custom_access_token_hook: {
        Args: { event: Json }
        Returns: Json
      }
      get_user_company_id: {
        Args: { p_user_id: string }
        Returns: string
      }
    }
    Enums: {
      [_ in never]: never
    }
    CompositeTypes: {
      [_ in never]: never
    }
  }
}

type DatabaseWithoutInternals = Omit<Database, "__InternalSupabase">

type DefaultSchema = DatabaseWithoutInternals[Extract<keyof Database, "public">]

export type Tables<
  DefaultSchemaTableNameOrOptions extends
    | keyof (DefaultSchema["Tables"] & DefaultSchema["Views"])
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof (DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
        DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Views"])
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? (DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
      DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Views"])[TableName] extends {
      Row: infer R
    }
    ? R
    : never
  : DefaultSchemaTableNameOrOptions extends keyof (DefaultSchema["Tables"] &
        DefaultSchema["Views"])
    ? (DefaultSchema["Tables"] &
        DefaultSchema["Views"])[DefaultSchemaTableNameOrOptions] extends {
        Row: infer R
      }
      ? R
      : never
    : never

export type TablesInsert<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Insert: infer I
    }
    ? I
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Insert: infer I
      }
      ? I
      : never
    : never

export type TablesUpdate<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Update: infer U
    }
    ? U
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Update: infer U
      }
      ? U
      : never
    : never

export type Enums<
  DefaultSchemaEnumNameOrOptions extends
    | keyof DefaultSchema["Enums"]
    | { schema: keyof DatabaseWithoutInternals },
  EnumName extends DefaultSchemaEnumNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"]
    : never = never,
> = DefaultSchemaEnumNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"][EnumName]
  : DefaultSchemaEnumNameOrOptions extends keyof DefaultSchema["Enums"]
    ? DefaultSchema["Enums"][DefaultSchemaEnumNameOrOptions]
    : never

export type CompositeTypes<
  PublicCompositeTypeNameOrOptions extends
    | keyof DefaultSchema["CompositeTypes"]
    | { schema: keyof DatabaseWithoutInternals },
  CompositeTypeName extends PublicCompositeTypeNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"]
    : never = never,
> = PublicCompositeTypeNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"][CompositeTypeName]
  : PublicCompositeTypeNameOrOptions extends keyof DefaultSchema["CompositeTypes"]
    ? DefaultSchema["CompositeTypes"][PublicCompositeTypeNameOrOptions]
    : never

export const Constants = {
  public: {
    Enums: {},
  },
} as const
